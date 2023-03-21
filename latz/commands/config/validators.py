from __future__ import annotations

import re
from typing import Any

import click
from pydantic import ValidationError

from ...plugins.manager import (
    SEARCH_BACKEND_SETTINGS_KEY,
    SEARCH_BACKEND_SETTINGS_MODEL,
)

FIELD_SEPARATOR = "."
VALUE_SEPARATOR = ","


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
            checked_values.update(
                self.validate_single_value(value, ctx.obj.config_class)
            )

        try:
            merge(checked_values, current_config)
            ctx.obj.config_class(**current_config)
        except ValidationError as exc:
            raise click.ClickException(f"\n{str(exc)}")

        return current_config

    def validate_single_value(self, value: str, config_class) -> dict:
        """
        Validates a single config parameter. This is done by first matching the
        string value against a regex. Afterwards we return this value in its dictionary
        representation (e.g. "param=value -> {"param": "value"}).

        :raises click.BadParameter: raises to halt program when bad input is received
        """
        match = self._pattern.match(value)

        if not match:
            raise click.BadParameter(self._format_bad_format_error(value))

        parameter, parsed_value = match.groups()
        schema = config_class.schema()
        parameter_type = get_param_type(schema, parameter)

        if parameter_type == tuple:
            parsed_value = parsed_value.split(VALUE_SEPARATOR)

        return get_nested_dict_from_path(parameter, parsed_value)

    @staticmethod
    def _format_bad_format_error(value):
        return (
            f"'{value}' does not conform to the correct format. Please use the 'param=value'"
            " format."
        )


def get_param_type(schema, parameter: str) -> type | None:
    """
    Tries to determine the parameter type based on the schema and the parameter name.

    TODO: This is currently
    """
    first_key, *other_keys = parameter.split(FIELD_SEPARATOR)

    if first_key == SEARCH_BACKEND_SETTINGS_KEY:
        second_key, *other_keys = other_keys
        backend_setting_schema = schema.get("definitions", {}).get(
            SEARCH_BACKEND_SETTINGS_MODEL
        )
        if backend_setting_schema is not None:
            default = (
                backend_setting_schema.get("properties", {})
                .get(second_key, {})
                .get("default")
            )
            if default is not None:
                third_key, *other_keys = other_keys
                return type(default.get(third_key))
    else:
        default = schema.get("properties", {}).get(first_key, {}).get("default")
        if default is not None:
            return type(default)

    raise click.BadParameter(f"'{parameter}' is not a valid configuration parameter")


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
    dotted_path_split = dotted_path.split(FIELD_SEPARATOR)
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

    parts = path.split(FIELD_SEPARATOR)
    return _inner(parts, value)


def merge(source, destination):
    """
    Recursively merges a dictionary.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination
