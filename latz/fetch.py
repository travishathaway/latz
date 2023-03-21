"""
Module which holds everything related to making networking requests for this application.
"""
import asyncio
import logging
from collections.abc import Iterable, Callable

import httpx

logger = logging.getLogger(__name__)


def get_async_client() -> httpx.AsyncClient:
    """
    Returns a httpx.Client object to use for making network requests.

    Note: this is currently pretty sparse but includes room to grow and allows us
    to add settings we wish to apply to all network requests for this particular
    application in the future.
    """
    return httpx.AsyncClient()


async def gather_results(get_callables: Iterable[Callable], limit: int = 10) -> tuple:
    """
    Downloads files asynchronously but limits concurrency to `limit`
    """
    sem = asyncio.Semaphore(limit)  # This allows us to limit our concurrency.

    async def _get(get_callable: Callable):
        async with sem:
            try:
                return await get_callable()
            except httpx.HTTPError as exc:
                logger.error(exc)

    tasks = tuple(_get(get_callable) for get_callable in get_callables)
    return await asyncio.gather(*tasks)
