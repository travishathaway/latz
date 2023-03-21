from argparse import Namespace
from typing import cast

import rich_click as click
from pydantic import create_model, validator

from .commands import search_command, config_group
from .config import get_app_config, BaseAppConfig
from .constants import CONFIG_FILES
from .exceptions import ConfigError
from .plugins.manager import get_plugin_manager, AppPluginManager

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN_EMOJI = True


def create_app_config_class(plugin_manager: AppPluginManager) -> type[BaseAppConfig]:
    """Creates the class that we use to create our application configuration object"""
    # We need to dynamically define our validators because we do not know all the of the
    # valid backends until runtime.
    validators = {
        "backend_validator": validator("search_backends", allow_reuse=True)(
            plugin_manager.get_backend_validator_func()
        )
    }

    # Dynamically create our new configuration object based on possible new fields
    # from our registered plugins.
    return cast(
        type[BaseAppConfig],
        create_model(
            "AppConfig",
            **plugin_manager.search_backend_config_fields,
            __validators__=validators,
            __base__=BaseAppConfig
        ),
    )


@click.group("latz")
@click.pass_context
def cli(ctx):
    """
    "latz" is a command line tool for searching images via various image API backends.
    It is largely meant for educational purposes to show how to develop plugin friendly
    Python applications.

    The included commands are "search" for performing actual image searches and "config"
    for setting and displaying configuration variables.
    """
    ctx.ensure_object(Namespace)
    plugin_manager = get_plugin_manager()
    ctx.obj.plugin_manager = plugin_manager

    AppConfig = create_app_config_class(plugin_manager)
    ctx.obj.config_class = AppConfig

    # Creates the actual config object which parses all possible configuration sources
    # listed in `CONFIG_FILES`.
    try:
        ctx.obj.config = get_app_config(CONFIG_FILES, AppConfig)
    except ConfigError as exc:
        raise click.ClickException(str(exc))


cli.add_command(search_command)
cli.add_command(config_group)
