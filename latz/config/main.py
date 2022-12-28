from __future__ import annotations

import json
import logging
from collections.abc import Sequence, Iterable
from pathlib import Path
from functools import reduce

from pydantic import ValidationError, BaseModel
from click import ClickException

from .models import BaseAppConfig
from .errors import format_validation_error, format_all_validation_errors

logger = logging.getLogger(__name__)


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
) -> tuple[tuple[dict | None, Path], str | None]:
    """
    Given a path, try to parse it as JSON and ensure it is a dictionary
    and then return it. If it fails, we log a warning and return ``None``
    """
    try:
        config_data_json = json.load(path.open())
    except json.JSONDecodeError as exc:
        return (None, path), f"Unable to parse {path}: {exc}"

    if not isinstance(config_data_json, dict):
        return (None, path), f"Unable to parse {path}: JSON not correctly formatted"

    return (config_data_json, path), None


def parse_app_config_model(
    data: dict, path: Path, model_class: type[BaseModel]
) -> tuple[BaseModel | None, str | None]:
    """
    Attempts to parse a dictionary as a ``AppConfig`` object. If successful,
    returns the ``AppConfig`` object and ``None`` as the error value. If not,
    returns ``None`` as the config and ``str`` as an error value.
    """
    try:
        config_model = model_class(**data)
        return config_model, None
    except ValidationError as exc:
        return None, format_validation_error(exc, path)


def get_app_config(
    paths: Sequence[Path], model_class: type[BaseAppConfig]
) -> BaseAppConfig:
    """
    Given a sequence of ``paths`` first attempts to parse these as JSON and then
    attempts to parse valid JSON objects as ``AppConfig`` objects.

    :raises ClickException: Happens when any errors are encountered during config parsing
    """
    existing_paths = tuple(path for path in paths if path.is_file())

    if not existing_paths:
        return model_class()

    # Parse JSON objects
    json_data_and_path, parse_errors = tuple(
        zip(*(parse_config_file_as_json(path) for path in existing_paths))
    )

    if not json_data_and_path:
        return model_class()

    # Parse AppConfig objects
    app_configs, config_parse_errors = tuple(
        zip(
            *(
                parse_app_config_model(data, path, model_class)
                for data, path in json_data_and_path
                if data
            )
        )
    )

    # Gather errors
    errors: tuple[str, ...] = tuple(filter(None, parse_errors + config_parse_errors))

    # Fail loudly if any errors
    if len(errors) > 0:
        raise ClickException(format_all_validation_errors(errors))

    # If there are no app_configs and no errors, provide a default
    if not app_configs:
        return model_class()

    # Merge all successfully parsed app_configs
    return merge_app_configs(app_configs, model_class)
