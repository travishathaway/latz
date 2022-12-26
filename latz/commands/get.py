from typing import cast

import click

from ..config.models import AppConfig


@click.command("get")
@click.argument("search")
@click.pass_context
def command(ctx, search: str):
    """
    Command that retrieves an image based on a search term
    """
    config = cast(AppConfig, ctx.obj.config)

    print(config.backend)
    print(search)
