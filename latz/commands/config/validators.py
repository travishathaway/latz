from __future__ import annotations

import re
from typing import Any

import click
from pydantic import ValidationError


def validate_and_parse_config_values(ctx, _, values) -> dict[str, str]:
    """
    Validation function that parses and validates incoming configure parameter that
    look like this:
        param=value
        nested.param=value
    """
    pattern = re.compile(r"([a-z,A-Z,\.,_]+)=(.*)")

    current_config = ctx.obj.config.dict()
    checked_values = {}

    for value in values:
        match = pattern.match(value)
        if not match:
            raise click.BadParameter(
                f"'{value}' does not conform to the correct format. Please use the 'param=value'"
                " format."
            )
        parameter, value = match.groups()
        current_value = get_dotted_path_value(current_config, parameter)
        if not current_value:
            raise click.BadParameter(
                f"'{parameter}' is not a valid configuration parameter"
            )
        checked_values.update(get_nested_dict_from_path(parameter, value))

    try:
        ctx.obj.config_class(**{**current_config, **checked_values})
    except ValidationError as exc:
        raise click.ClickException(f"\n{str(exc)}")

    return checked_values


def get_dotted_path_value(nest: dict, dotted_path: str) -> Any:
    """
    When provides a ``dotted_path`` like "a.b.c" returns the nested value in ``nest``

    Example:
    >>> get_dotted_path_value({"a": {"b": {"c": 1}}}, "a.b.c.")
    1
    >>> get_dotted_path_value({"a": {"b": {"c": 1}}}, "a.b.c.d")  # We go as deep as we can
    1
    >>> get_dotted_path_value({"a": {"b": {"c": 1}}}, "d.c.b.a")

    """
    dotted_path_split = dotted_path.split(".")
    current_nest = nest

    for key_val in dotted_path_split:
        sub_val = current_nest.get(key_val)
        if not isinstance(sub_val, dict):
            return sub_val
        else:
            current_nest = sub_val


def get_nested_dict_from_path(path: str, value: Any) -> dict:
    """
    Used to transform our input config parameter "paths" (e.g. "nested.config.param")
    to an expanded dictionary.

    This only supports dictionaries that are structured like dict[str, dict[str, str]].

    Python's recursion limits prohibit deeply nested paths (> 999), but practically,
    this

    Examples:
        >>> get_nested_dict_from_path("nested.config.value", 123)
        {'nested': {'config': {'value': 123}}}
        >>> get_nested_dict_from_path("parameter", 123)
        {'parameter': 123}
        >>> get_nested_dict_from_path("", 123)
        {}
    """
    if not path:
        return {}

    def _inner(_parts: list[str], _value: Any) -> dict:
        if not _parts:
            return _value

        nested_dict = {}
        key = _parts.pop(0)
        nested_dict[key] = _inner(_parts, _value)

        return nested_dict

    parts = path.split(".")
    return _inner(parts, value)
