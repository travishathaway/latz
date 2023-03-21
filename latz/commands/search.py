import asyncio
from collections.abc import Iterable, Callable
from functools import partial

import click
from rich import print as rprint

from latz import fetch


async def main(search_callables: Iterable[Callable]):
    """
    Main async coroutine that runs all the currently configured search functions
    and prints the output of the query.
    """
    results = await fetch.gather_results(search_callables)
    rprint(results)


@click.command("search")
@click.argument("query")
@click.pass_context
def command(ctx, query: str):
    """
    Command that retrieves an image based on a search term
    """
    client = fetch.get_async_client()
    search_backends = ctx.obj.plugin_manager.get_configured_search_backends(
        ctx.obj.config
    )

    search_callables = (
        partial(backend.search, client, ctx.obj.config, query)
        for backend in search_backends
    )

    asyncio.run(main(search_callables))
