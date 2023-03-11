import click
from rich import print as rprint

from latz.fetch import get_fetch_client
from latz.exceptions import ImageAPIError


@click.command("search")
@click.argument("query")
@click.pass_context
def command(ctx, query: str):
    """
    Command that retrieves an image based on a search term
    """
    client = get_fetch_client()

    try:
        result_set = []

        for search_backend in ctx.obj.plugin_manager.hook.search_backend():
            result_set.append(search_backend.search(client, ctx.obj.config, query))
    except ImageAPIError as exc:
        raise click.ClickException(str(exc))

    for res in result_set:
        rprint(res)
