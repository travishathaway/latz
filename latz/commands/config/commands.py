from __future__ import annotations

from pathlib import Path

import rich_click as click
from rich import print as rprint

from ...constants import CONFIG_FILE_HOME_DIR
from ...config import parse_config_file_as_json, write_config_file
from ...exceptions import ConfigError
from .validators import ConfigValuesValidator

# Create our validator callables
validate_and_parse_config_values = ConfigValuesValidator()


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
    "-c",
    "--config",
    type=click.Path(exists=True),
    help="Path of config file to write to. Defaults to ~/.latz.json",
)
def set_command(config, config_values):
    """
    Set configuration values.
    """
    config_file = Path(config or CONFIG_FILE_HOME_DIR)

    # If this file does not exist, write an empty JSON object to it
    if not config_file.exists():
        with config_file.open("w") as fp:
            fp.write("{}")

    parsed_config = parse_config_file_as_json(config_file)

    if parsed_config.error is not None:
        raise click.ClickException(parsed_config.error)

    # Merge the new values and old values; new overwrites the old
    new_config_file_data = {**parsed_config.data, **config_values}

    try:
        write_config_file(new_config_file_data, config_file)
    except ConfigError as exc:
        raise click.ClickException(str(exc))


group.add_command(show_command)
group.add_command(set_command)
