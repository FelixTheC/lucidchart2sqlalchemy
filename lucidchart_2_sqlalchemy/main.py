from pathlib import Path

import typer as typer

from lucidchart_2_sqlalchemy.parser import main
from lucidchart_2_sqlalchemy.utils import display_settings, get_json_data, save_json_data

app = typer.Typer()


def complete_languages(ctx: typer.Context, language: str):
    return "de", "en"


@app.command()
def display_config():
    json_data = get_json_data()
    display_settings(json_data)


@app.command()
def set_config_file_path(
    file_path: str = typer.Argument(..., help="Only the folder-name is required.")
):
    json_data = get_json_data()
    json_data["base_folder"] = file_path
    save_json_data(json_data)


@app.command()
def set_config_base_model_path(
    base_model_path: str = typer.Argument(..., help="app.models.modelbase")
):
    json_data = get_json_data()
    json_data["base_model_path"] = base_model_path
    save_json_data(json_data)


@app.command()
def set_config_default_base_model(default_base_model: str):
    json_data = get_json_data()
    json_data["default_base_model"] = default_base_model
    save_json_data(json_data)


@app.command()
def parse_csv(
    csv_file: Path,
    language: str = typer.Option(
        "", help="language setting in lucidchart", autocompletion=complete_languages
    ),
):
    main(csv_file, language)


if __name__ == "__main__":
    app()
