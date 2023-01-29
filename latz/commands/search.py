from collections.abc import Callable
from typing import cast, ContextManager, Any

import click
from rich import print as rprint

from latz.image import ImageAPI
from latz.exceptions import ImageAPIError


@click.command("search")
@click.argument("query")
@click.pass_context
def command(ctx, query: str):
    """
    Command that retrieves an image based on a search term
    """
    image_api_context_manager = cast(
        Callable[[Any], ContextManager[ImageAPI]], ctx.obj.image_api_context_manager
    )

    with image_api_context_manager(ctx.obj.config) as api:
        try:
            result_set = api.search(query)
        except ImageAPIError as exc:
            raise click.ClickException(str(exc))

        for res in result_set.results:
            rprint(res)
