from __future__ import annotations

import re
from typing import Any

import click
from pydantic import ValidationError


class ConfigValuesValidator:
    """
    Validation class that is meant to be called as a validator callable
    within click. It will parse and validate incoming values that look like
    this:

        param=value -> {"param": "value"}
        nested.param=value -> {"nested": {"param": "value"}}
    """

    def __init__(self):
        self._pattern = re.compile(r"([a-zA-Z._]+)=(.*)")

    def __call__(self, ctx, _, values) -> dict[str, str]:
        current_config = ctx.obj.config.dict()
        checked_values = {}

        for value in values:
            checked_values.update(self.validate_single_value(value))

        try:
            ctx.obj.config_class(**{**current_config, **checked_values})
        except ValidationError as exc:
            raise click.ClickException(f"\n{str(exc)}")

        return checked_values

    def validate_single_value(self, value: str) -> dict:
        """
        Validates a single config parameter. This is done by first matching the
        string value against a regex. Afterwards we return this value in its dictionary
        representation (e.g. "param=value -> {"param": "value"}).

        :raises click.BadParameter: raises to halt program when bad input is received
        """
        match = self._pattern.match(value)

        if not match:
            raise click.BadParameter(self._format_bad_format_error(value))

        parameter, value = match.groups()

        return get_nested_dict_from_path(parameter, value)

    @staticmethod
    def _format_bad_format_error(value):
        return (
            f"'{value}' does not conform to the correct format. Please use the 'param=value'"
            " format."
        )

    @staticmethod
    def _format_invalid_parameter_error(parameter):
        return f"'{parameter}' is not a valid configuration parameter"


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
