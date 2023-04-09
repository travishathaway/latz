import asyncio
from collections.abc import Iterable, Callable
from functools import partial
from itertools import chain

import click
from rich.console import Console
from rich.table import Table

from latz import fetch
from latz.image import ImageSearchResult


def display_results(results: Iterable[ImageSearchResult]) -> None:
    """
    Displays the `ImageSearchResultSet` objects as a `rich.table.Table`
    """
    table = Table(title="Search Results")

    table.add_column("#", no_wrap=True)
    table.add_column("Link", style="magenta")
    table.add_column("Backend", justify="right", style="green")

    for idx, result in enumerate(results, start=1):
        table.add_row(str(idx), result.url, result.search_backend)

    console = Console()
    console.print(table)


async def main(search_callables: Iterable[Callable]):
    """
    Main async coroutine that runs all the currently configured search functions
    and prints the output of the query.
    """
    results = await fetch.gather_results(search_callables)

    # merge results sets into single tuple
    results = tuple(chain(*results))

    display_results(results)


@click.command("search")
@click.argument("query")
@click.pass_context
def command(ctx, query: str):
    """
    Command that retrieves an image based on a search term
    """
    client = fetch.get_async_client()

    # We collect all enabled backends here
    search_backends = ctx.obj.plugin_manager.get_configured_search_backends(
        ctx.obj.config
    )

    # We use `partial` to create a generator with callables preconfigured with the
    # necessary arguments (e.g. `client`, `config` and `query`)
    search_callables = (
        partial(backend.search, client, ctx.obj.config, query)
        for backend in search_backends
    )

    # This is the function call that kicks everything off
    asyncio.run(main(search_callables))
