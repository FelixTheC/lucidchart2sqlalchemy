import json
from json import JSONDecodeError
from pathlib import Path

import sqlalchemy as sa
import typer
from strongtyping.strong_typing import match_typing

SQLALCHEMY_TYPES = {
    key.lower(): key
    for key in vars(vars(sa)["types"]).keys()
    if not key.startswith("_") and not key.swapcase().islower()
}

SQLALCHEMY_TYPES.update(
    {
        "str": SQLALCHEMY_TYPES["string"],
        "bool": SQLALCHEMY_TYPES["boolean"],
        "int": SQLALCHEMY_TYPES["integer"],
    }
)

COLUMN_NAMES = {
    "en": {
        "library": "Shape Library",
        "area_1": "Text Area 1",
        "area_2": "Text Area 2",
    },
    "de": {
        "library": "Formenbibliothek",
        "area_1": "Textbereich 1",
        "area_2": "Textbereich 2",
    },
}


def get_json_data() -> dict:
    with Path(Path(__file__).parent / "config.json").open("r") as file:
        try:
            return json.load(file)
        except JSONDecodeError:
            return {}


@match_typing
def save_json_data(json_data: dict):
    with Path("config.json").open("w") as file:
        json.dump(json_data, file)


def display_settings(data: dict, tab_level: int = 0):
    idx = 0
    tab = "\t" * tab_level
    for key, val in data.items():
        color = typer.colors.GREEN if idx % 2 == 0 else typer.colors.CYAN
        if isinstance(val, dict):
            typer.secho(f"{tab}{key}: ", fg=color)
            display_settings(val, tab_level=tab_level + 1)
        else:
            typer.secho(f"{tab}{key}: {val}", fg=color)
        idx += 1
