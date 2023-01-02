from __future__ import annotations

import json
import logging
from collections.abc import Sequence, Iterable
from pathlib import Path
from functools import reduce
from typing import NamedTuple, Any

from pydantic import ValidationError

from .models import BaseAppConfig
from .errors import format_validation_error, format_all_validation_errors

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


class ParsedConfigFile(NamedTuple):
    #: Path to the configuration file
    path: Path

    #: Data contained within the configuration file
    data: dict | None

    #: Parse errors encountered while parsing the configuration file
    error: str | None

    #: Parse errors encountered while parsing the configuration file
    model: BaseAppConfig | None


def merge_app_configs(
    app_configs: Iterable[BaseAppConfig], model_class: type[BaseAppConfig]
) -> BaseAppConfig:
    def reduce_func(
        config_one: BaseAppConfig, config_two: BaseAppConfig
    ) -> BaseAppConfig:
        """
        Provided two AppConfig objects, merge them into a single AppConfig object.
        Properties from ``config_two`` will override properties on ``config_one``
        """
        return model_class(**{**config_one.dict(), **config_two.dict()})

    return reduce(reduce_func, app_configs)


def parse_config_file_as_json(
    path: Path,
) -> ParsedConfigFile:
    """
    Given a path, try to parse it as JSON and ensure it is a dictionary
    and then return it. If it fails, we log a warning and return ``None``
    """
    try:
        with path.open() as fp:
            config_data_json = json.load(fp)
    except json.JSONDecodeError as exc:
        return ParsedConfigFile(
            data=None, path=path, error=f"Unable to parse {path}: {exc}", model=None
        )

    if not isinstance(config_data_json, dict):
        return ParsedConfigFile(
            data=None,
            path=path,
            error=f"Unable to parse {path}: JSON not correctly formatted",
            model=None,
        )

    return ParsedConfigFile(data=config_data_json, path=path, error=None, model=None)


def parse_app_config_model(
    parsed_config: ParsedConfigFile, model_class: type[BaseAppConfig]
) -> ParsedConfigFile:
    """
    Attempts to parse a dictionary as a ``AppConfig`` object. If successful,
    returns the ``AppConfig`` object and ``None`` as the error value. If not,
    returns ``None`` as the config and ``str`` as an error value.
    """
    try:
        if parsed_config.data:
            config_model = model_class(**parsed_config.data)
            return ParsedConfigFile(
                model=config_model, error=None, path=parsed_config.path, data=None
            )
        else:
            return ParsedConfigFile(
                model=None,
                path=parsed_config.path,
                error=parsed_config.error,
                data=None,
            )
    except ValidationError as exc:
        return ParsedConfigFile(
            model=None,
            error=format_validation_error(exc, parsed_config.path),
            data=parsed_config.data,
            path=parsed_config.path,
        )


def parse_config_files(paths: Sequence[Path]) -> tuple[ParsedConfigFile, ...] | None:
    """
    Given a list a ``paths`` to configuration files, returns those which
    can successfully be parsed. These are returned as ``ParsedConfigFile`` objects
    which contain the attributes "path", "data", and "error".
    """
    existing_paths = tuple(path for path in paths if path.is_file())

    if not existing_paths:
        return  # type: ignore

    # Parse JSON objects
    return tuple(parse_config_file_as_json(path) for path in existing_paths)


def get_app_config(
    paths: Sequence[Path], model_class: type[BaseAppConfig]
) -> BaseAppConfig:
    """
    Given a sequence of ``paths`` first attempts to parse these as JSON and then
    attempts to parse valid JSON objects as ``AppConfig`` objects.

    :raises ConfigError: Happens when any errors are encountered during config parsing
    """
    parsed_config_files = parse_config_files(paths)

    # No files were found 🤷‍; let's return a default config object
    if parsed_config_files is None:
        return model_class()

    parsed_config_files = tuple(
        parse_app_config_model(parsed, model_class) for parsed in parsed_config_files
    )

    # Gather errors
    errors = tuple(parsed.error for parsed in parsed_config_files if parsed.error)

    # Fail loudly if any errors
    if len(errors) > 0:
        raise ConfigError(format_all_validation_errors(errors))

    # Gather configs
    app_configs = tuple(parsed.model for parsed in parsed_config_files if parsed.model)

    # If there are no app_configs and no errors, provide a default
    if not app_configs:
        return model_class()

    # Merge all successfully parsed app_configs
    return merge_app_configs(app_configs, model_class)


def write_config_file(config_file_data: dict[str, Any], config_file: Path) -> None:
    """
    Attempts to write config file and returns the exception as a string if it failed.

    :raises ConfigError: Raised when we are not able to write our config file.
    """
    try:
        with config_file.open("w") as fp:
            json.dump(config_file_data, fp, indent=2)
    except OSError as exc:
        raise ConfigError(str(exc))
