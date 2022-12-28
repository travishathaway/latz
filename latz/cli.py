from argparse import Namespace
from typing import cast

import rich_click as click
from pydantic import create_model

from .commands import search_command
from .config import get_app_config, BaseAppConfig
from .constants import CONFIG_FILES
from .plugins.manager import get_plugin_manager

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN_EMOJI = True


@click.group()
@click.pass_context
def cli(ctx):
    """
    Creates a click command group but also does the job of properly initializing
    our command line application.
    """
    ctx.ensure_object(Namespace)
    plugin_manager = get_plugin_manager()

    # Dynamically create our new configuration object based on possible new fields
    # from our registered plugins.
    AppConfig = cast(
        type[BaseAppConfig],
        create_model(
            "AppConfig",
            **plugin_manager.image_api_config_fields,
            __base__=BaseAppConfig
        ),
    )

    # Creates the actual config object which parses all possible configuration sources
    # listed in ``CONFIG_FILES``.
    app_config = get_app_config(CONFIG_FILES, AppConfig)

    # Attach several properties to click's ``ctx`` object so that we have access to it
    # in our sub-commands.
    ctx.obj.config = app_config
    ctx.obj.image_api_context_manager = plugin_manager.get_image_api_context_manager(
        app_config
    )


cli.add_command(search_command)
