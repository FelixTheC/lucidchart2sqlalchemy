import re
from pathlib import Path
from typing import List, Literal, Tuple

import pandas as pd
import typer
from strongtyping.strong_typing import match_typing

from lucidchart_2_sqlalchemy.utils import COLUMN_NAMES, SQLALCHEMY_TYPES, get_json_data

_CONFIG = get_json_data()
_TAB = "    "
_BASE_FOLDER = Path(_CONFIG.get("base_folder", ""))

if not _BASE_FOLDER.exists():
    _BASE_FOLDER.mkdir(parents=True)


class SqlAlchemyObject:
    table_name: str
    class_name: str
    base_class_name: str
    fields: list[tuple]

    def __init__(self, table_name: str, class_name: str, base_class_name, fields: list):
        self.table_name = table_name
        self.class_name = class_name
        self.base_class_name = base_class_name
        self.fields = fields

    def __write_imports(self):
        imports = [
            "import sqlalchemy as sa",
            f"from {_CONFIG['base_model_path']} import {self.base_class_name}",
            "\n\n",
        ]
        return "\n".join(imports)

    def __write_class_definition(self):
        return f"class {self.class_name}({self.base_class_name}):\n"

    def __write_table_definition(self):
        return f'{_TAB}__tablename__ = "{self.table_name}"\n'

    def __write_field_definitions(self):
        field_definitions = []
        for field in self.fields:
            if len(field) < 2:
                continue
            name, type_ = field
            sqlalchemy_field = SQLALCHEMY_TYPES[type_]
            val, name = self.__optional_parameters(name)
            default, name = self.__default_or_on_update(name)

            if "_id" in name:
                reference_name = name.replace("_id", ".id")
                field_definitions.append(
                    f'{_TAB}{name}: {type_} = sa.Column(sa.{sqlalchemy_field}, sa.ForeignKey("{reference_name}"){val}'  # noqa: E501
                )
            else:
                line = f"{_TAB}{name}: {type_} = sa.Column(sa.{sqlalchemy_field}{val}"
                field_definitions.append(line)
        return "\n".join(field_definitions)

    def __optional_parameters(self, name):
        match [name[val] for val in range(2)]:
            case ["*", "*"]:
                return self.__primary_key(name[2:]), name[2:]
            case ["*", _]:
                return self.__nullable(), name[1:]
            case _:
                return ")", name

    def __primary_key(self, name):
        if SQLALCHEMY_TYPES[name] in (SQLALCHEMY_TYPES("INT"),
                                      SQLALCHEMY_TYPES["SMALLINT"],
                                      SQLALCHEMY_TYPES["BIGINT"]):
            return "primary_key=True, autoincrement=True"
        return "primary_key=True"

    def __nullable(self):
        return f", nullable=False)"

    def __default_or_on_update(self, name):
        if "=" in name:
            name, default = name.split("=", maxsplit=2)
            return f"default={default.strip()}", name.strip()
        elif "^=" in name:
            name, default = name.split("^=", maxsplit=2)
            return f"onupdate={default.strip()}", name.strip()
        else:
            return "", name

    def generate_file(self):
        with (_BASE_FOLDER / Path(f"{self.table_name}.py")).open("w") as file:
            file.writelines(self.__write_imports())
            file.write(self.__write_class_definition())
            file.write(self.__write_table_definition())
            file.write("\n")
            file.writelines(self.__write_field_definitions())
            file.write("\n")


def _extract_parent_class(name: str) -> Tuple[str, str]:
    if "(" not in name:
        return name, _CONFIG.get("default_base_model", "")
    else:
        cls_name, tmp_parent_class = name.split("(")
        parent_class = tmp_parent_class.removesuffix(")")
        return cls_name, parent_class


def _generate_table_name(name: str) -> str:
    start_char = [char.lower() for char in re.findall(r"[A-Z]", name)]
    word_parts = re.split(r"[A-Z]", name)[1:]
    words = [x + y for x, y in zip(start_char, word_parts)]
    return "_".join(words)


def _generate_columns(data: str) -> List[Tuple[str, str]]:
    return [tuple(val.replace(" ", "").split(":")) for val in data.split("\n")]


def _generate_sqlalchemy_object(name: str, fields: str):
    cls_name, parent_cls = _extract_parent_class(name)
    return SqlAlchemyObject(
        _generate_table_name(cls_name), cls_name, parent_cls, _generate_columns(fields)
    )


@match_typing
def main(csv_file: Path, language: Literal["de", "en"]):
    if not _BASE_FOLDER:
        typer.secho("Please run set_config_file_path.", fg=typer.colors.RED)
        raise typer.Abort()

    df = pd.read_csv(csv_file)
    tmp_df = df[df[COLUMN_NAMES[language]["library"]] == "UML"]
    uml_df = tmp_df[[COLUMN_NAMES[language]["area_1"], COLUMN_NAMES[language]["area_2"]]]

    objs = []

    for row in uml_df.iterrows():
        _, data = row
        name, fields = data
        objs.append(_generate_sqlalchemy_object(name, fields))

    for obj in objs:
        obj.generate_file()


if __name__ == "__main__":
    main(Path("../CamperVanPricing_en_v2.csv"), "en")
