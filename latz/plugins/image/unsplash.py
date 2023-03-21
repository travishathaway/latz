from __future__ import annotations

import urllib.parse

import httpx
from pydantic import BaseModel, Field

from ...image import (
    ImageSearchResult,
    ImageSearchResultSet,
)
from .. import hookimpl, SearchBackendHook
from ...exceptions import SearchBackendError

#: Name of the plugin that will be referenced in our configuration
PLUGIN_NAME = "unsplash"

#: Base URL for the Unsplash API
BASE_URL = "https://api.unsplash.com/"

#: Endpoint used for searching images
SEARCH_ENDPOINT = urllib.parse.urljoin(BASE_URL, "/search/photos")


class UnsplashBackendConfig(BaseModel):
    """
    Unsplash requires the usage of an ``access_key`` and ``secret_key``
    when using their API. We expose these settings here so users of the CLI
    tool can use it.
    """

    access_key: str = Field(description="Access key for the Unsplash API")


async def _get(client: httpx.AsyncClient, url: str, query: str) -> dict:
    """
    Wraps `client.get` call in a try, except so that we raise
    an application specific exception instead.

    :raises SearchBackendError: Encountered during problems querying the API
    """
    try:
        resp = await client.get(url, params={"query": query})
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise SearchBackendError(str(exc), original=exc)

    json_data = resp.json()

    if not isinstance(json_data, dict):
        raise SearchBackendError("Received malformed response from search backend")

    return json_data


async def search(client: httpx.AsyncClient, config, query: str) -> ImageSearchResultSet:
    """
    Find images based on a `query` and return an `ImageSearchResultSet`

    :raises SearchBackendError: Encountered during problems querying the API
    """
    client.headers = httpx.Headers(
        {
            "Authorization": f"Client-ID {config.search_backend_settings.unsplash.access_key}"
        }
    )
    json_data = await _get(client, SEARCH_ENDPOINT, query)

    search_results = tuple(
        ImageSearchResult(
            url=record.get("links", {}).get("download"),
            width=record.get("width"),
            height=record.get("height"),
        )
        for record in json_data.get("results", tuple())
    )

    return ImageSearchResultSet(
        search_results, len(search_results), search_backend=PLUGIN_NAME
    )


@hookimpl
def search_backend():
    """
    Registers our Unsplash image API backend
    """
    return SearchBackendHook(
        name=PLUGIN_NAME,
        search=search,
        config_fields=UnsplashBackendConfig(access_key=""),
    )
