from argparse import Namespace
from typing import cast

import rich_click as click
from click import ClickException
from pydantic import create_model

from .commands import get_command
from .config import get_app_config, BaseAppConfig
from .constants import CONFIG_FILES
from .plugins.manager import get_plugin_manager
from .plugins.types import ImageAPIPlugin

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN_EMOJI = True


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(Namespace)
    plugin_manager = get_plugin_manager()

    image_search_apis: list[ImageAPIPlugin] = plugin_manager.hook.image_search_api()

    config_fields = {}
    image_backend_names = []

    for search_api in image_search_apis:
        image_backend_names.append(search_api.name)
        config_fields.update(search_api.config_fields)

    AppConfig = cast(
        type[BaseAppConfig],
        create_model("AppConfig", **config_fields, __base__=BaseAppConfig),
    )

    app_config = get_app_config(CONFIG_FILES, AppConfig)

    image_search_api = None

    for search_api in image_search_apis:
        if search_api.name == app_config.backend:
            image_search_api = search_api.backend.create(app_config)

    if image_search_api is None:
        raise ClickException(
            "Backend has been improperly configure. Please choose from the available"
            f" backends: {','.join(image_backend_names)}"
        )

    ctx.obj.config = app_config
    ctx.obj.image_search_api = image_search_api
    ctx.obj.config_class = AppConfig


cli.add_command(get_command)


if __name__ == "__main__":
    cli()
