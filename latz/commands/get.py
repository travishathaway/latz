from typing import cast

import click

from ..image import ImageAPI


@click.command("get")
@click.argument("search")
@click.pass_context
def command(ctx, search: str):
    """
    Command that retrieves an image based on a search term
    """
    image_search_api = cast(ImageAPI, ctx.obj.image_search_api)

    results = image_search_api.search(search)

    print(results)
