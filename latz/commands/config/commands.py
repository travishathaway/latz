from __future__ import annotations

import json

import rich_click as click
from rich import print as rprint

from ...constants import CONFIG_FILE_CWD, CONFIG_FILE_HOME_DIR
from .validators import validate_and_parse_config_values


@click.group("config")
def group():
    """Various commands for showing and setting configuration values"""


@click.command("show")
@click.pass_context
def show_command(ctx):
    """Prints the current config"""
    rprint(ctx.obj.config.json(indent=2))


@click.command("set")
@click.argument("config_values", nargs=-1, callback=validate_and_parse_config_values)
@click.option(
    "-h",
    "--home",
    is_flag=True,
    help="Write to home directory config file instead of in current working directory",
)
def set_command(home, config_values):
    """
    Set configuration values.
    """
    config_file = CONFIG_FILE_HOME_DIR if home else CONFIG_FILE_CWD
    bad_json = False

    with config_file.open("r") as fp:
        try:
            config_file_data = json.load(fp)
        except json.JSONDecodeError:
            # TODO: this needs to be refactored so we aren't repeating this twice.
            raise click.ClickException(
                f"Config file: {config_file} has been corrupted (i.e. not in the correct format) "
                "and cannot be edited."
            )

    if not isinstance(config_file_data, dict) or bad_json:
        raise click.ClickException(
            f"Config file: {config_file} has been corrupted (i.e. not in the correct format) "
            "and cannot be edited."
        )

    # Merge the new values and old values; new overwrites the old
    new_config_file_data = {**config_file_data, **config_values}

    with config_file.open("w") as fp:
        json.dump(new_config_file_data, fp, indent=2)


group.add_command(show_command)
group.add_command(set_command)
