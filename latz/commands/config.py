from __future__ import annotations

import re
from typing import Any

import rich_click as click
from click import BadParameter, ClickException
from pydantic import ValidationError
from rich import print as rprint

from ..constants import CONFIG_FILE_CWD, CONFIG_FILE_HOME_DIR


@click.group("config")
def group():
    """Various commands for showing and setting configuration values"""


@click.command("show")
@click.pass_context
def show_command(ctx):
    """Prints the current config"""
    rprint(ctx.obj.config.json(indent=2))


def get_dotted_path_value(nest: dict, dotted_path: str) -> Any:
    """
    When provides a ``dotted_path`` like "a.b.c" returns the nested value in ``nest``

    Example:
    >>> get_dotted_path_value({"a": {"b": {"c": 1}}}, "a.b.c.")
    1
    >>> get_dotted_path_value({"a": {"b": {"c": 1}}}, "a.b.c.d")  # We go as deep as we can
    1
    >>> get_dotted_path_value({"a": {"b": {"c": 1}}}, "d.c.b.a")
    None
    """
    dotted_path_split = dotted_path.split(".")
    current_nest = nest

    for key_val in dotted_path_split:
        sub_val = current_nest.get(key_val)
        if not isinstance(sub_val, dict):
            return sub_val
        else:
            current_nest = sub_val


def validate_and_parse_config_values(ctx, _, values) -> dict[str, str]:
    """
    Validation function that parses and validates incoming configure parameter that
    look like this:
        param=value
        nested.param=value
    """
    pattern = re.compile(r"([a-z,A-Z,\.]+)=(.*)")

    current_config = ctx.obj.config.dict()
    checked_values = {}

    for value in values:
        match = pattern.match(value)
        if not match:
            raise BadParameter(
                f"'{value}' does not conform to the correct format. Please use the 'param=value'"
                " format."
            )
        parameter, value = match.groups()
        current_value = get_dotted_path_value(current_config, parameter)
        if not current_value:
            raise BadParameter(f"'{parameter}' is not a valid configuration parameter")
        checked_values.update(get_nested_dict_from_path(parameter, value))

    try:
        ctx.obj.config_class(**{**current_config, **checked_values})
    except ValidationError as exc:
        raise ClickException(f"\n{str(exc)}")

    return checked_values


def get_nested_dict_from_path(path: str, value: Any) -> dict:
    """
    Given an input that looks like this:

        "a.b.c", 123

    Return an output that looks like this:

        {"a": {"b": {"c": 123}}}

    Examples:
        >>> get_nested_dict_from_path("a.b.c", 123)
        {"a": {"b": {"c": 123}}}
        >>> get_nested_dict_from_path("a", 123)
        {"a": 123}
        >>> get_nested_dict_from_path("", 123)
        {}
    """

    def _graph_from_str(_parts):
        graph = {}
        for idx, key in enumerate(_parts):
            if len(parts) == idx + 1:
                graph[key] = None
            else:
                graph[key] = _parts[idx + 1]
        return graph

    def _get_nested_dict(graph, nodes, _value):
        if not nodes:
            return _value
        return {
            node: _get_nested_dict(graph, graph.get(node, []), _value) for node in nodes
        }

    parts = path.split(".")

    if len(parts) == 0:
        return {}
    if len(parts) == 1:
        return {parts[0]: value}

    return _get_nested_dict(_graph_from_str(parts), [parts[0]], value)


@click.command("set")
@click.argument("config_values", nargs=-1, callback=validate_and_parse_config_values)
@click.option(
    "-h",
    "--home",
    is_flag=True,
    help="Write to home directory config file instead of in current working directory",
)
@click.pass_context
def set_command(ctx, home, config_values):
    """Set configuration values"""
    config_file = CONFIG_FILE_HOME_DIR if home else CONFIG_FILE_CWD

    print(config_file)


group.add_command(show_command)
group.add_command(set_command)
