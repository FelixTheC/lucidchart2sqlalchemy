import re
from pathlib import Path
from typing import List
from typing import Literal
from typing import Tuple

import pandas as pd
import toml

from src.utils import COLUMN_NAMES
from src.utils import SQLALCHEMY_TYPES

_config = toml.load(Path(__file__).parent.parent / Path("pyproject.toml"))
_CONFIG = _config["lucid2sqlalchemy"]
TAB = "    "
_BASE_FOLDER = Path(__file__).parent.parent / Path("lucidchart_models")

if not _BASE_FOLDER.exists():
    _BASE_FOLDER.mkdir()


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
        imports = ["import sqlalchemy as sa",
                   f"from {_CONFIG['base_model']} import {self.base_class_name}",
                   "\n\n"]
        return '\n'.join(imports)

    def __write_class_definition(self):
        return f"class {self.class_name}({self.base_class_name}):\n"

    def __write_table_definition(self):
        return f'{TAB}__tablename__ = "{self.table_name}"\n'

    def __write_field_definitions(self):
        field_definitions = []
        for field in self.fields:
            if len(field) < 2:
                continue
            name, type_ = field
            sqlalchemy_field = SQLALCHEMY_TYPES[type_]
            if "_id" in name:
                reference_name = name.replace("_id", ".id")
                field_definitions.append(
                    f'{TAB}{name}: {type_} = sa.Column(sa.{sqlalchemy_field}, sa.ForeignKey("{reference_name}"))')
            else:
                field_definitions.append(f"{TAB}{name}: {type_} = sa.Column(sa.{sqlalchemy_field})")
        return "\n".join(field_definitions)

    def generate_file(self):
        with (_BASE_FOLDER / Path(f"{self.table_name}.py")).open("w") as file:
            file.writelines(self.__write_imports())
            file.write(self.__write_class_definition())
            file.write(self.__write_table_definition())
            file.write("\n")
            file.writelines(self.__write_field_definitions())
            file.write("\n")


def extract_parent_class(name: str) -> Tuple[str, str]:
    if not "(" in name:
        return name, _CONFIG.get('default_base_model', "")
    else:
        cls_name, tmp_parent_class = name.split("(")
        parent_class = tmp_parent_class.removesuffix(")")
        return cls_name, parent_class


def generate_table_name(name: str) -> str:
    start_char = [char.lower() for char in re.findall(r"[A-Z]", name)]
    word_parts = re.split(r"[A-Z]", name)[1:]
    words = [x + y for x, y in zip(start_char, word_parts)]
    return "_".join(words)


def generate_columns(data: str) -> List[Tuple[str, str]]:
    return [tuple(val.replace(" ", "").split(":")) for val in data.split("\n")]


def generate_sqlalchemy_object(name: str, fields: str):
    cls_name, parent_cls = extract_parent_class(name)
    return SqlAlchemyObject(generate_table_name(cls_name), cls_name, parent_cls, generate_columns(fields))


def main(csv_file: Path, language: Literal["de", "en"]):
    df = pd.read_csv(csv_file)
    tmp_df = df[df[COLUMN_NAMES[language]["library"]] == "UML"]
    uml_df = tmp_df[[COLUMN_NAMES[language]["area_1"], COLUMN_NAMES[language]["area_2"]]]

    objs = []

    for row in uml_df.iterrows():
        _, data = row
        name, fields = data
        objs.append(generate_sqlalchemy_object(name, fields))

    for obj in objs:
        obj.generate_file()


if __name__ == '__main__':
    main(Path("../CamperVanPricing_en_v2.csv"), "en")
