from __future__ import annotations

import urllib.parse

import httpx
from pydantic import BaseModel, Field

from ...image import (
    ImageSearchResult,
    ImageSearchResultSet,
)
from .. import hookimpl, SearchBackendHook
from ...exceptions import ImageAPIError

#: Name of the plugin that will be referenced in our configuration
PLUGIN_NAME = "unsplash"


class UnsplashBackendConfig(BaseModel):
    """
    Unsplash requires the usage of an ``access_key`` and ``secret_key``
    when using their API. We expose these settings here so users of the CLI
    tool can use it.
    """

    access_key: str = Field(description="Access key for the Unsplash API")


#: These are the configuration settings we export when registering our plugin
CONFIG_FIELDS = {PLUGIN_NAME: (UnsplashBackendConfig, {"access_key": ""})}

#: Base URL for the Unsplash API
BASE_URL = "https://api.unsplash.com/"

#: Endpoint used for searching images
SEARCH_ENDPOINT = "/search/photos"


def search(client: httpx.Client, config, query: str) -> ImageSearchResultSet:
    """
    Find images based on a ``search_term`` and return an ``ImageSearchResultSet``

    :raises HTTPError: Encountered during problems querying the API
    """
    client.headers = httpx.Headers(
        {
            "Authorization": f"Client-ID {config.search_backend_settings.unsplash.access_key}"
        }
    )
    search_url = urllib.parse.urljoin(BASE_URL, SEARCH_ENDPOINT)

    try:
        resp = client.get(search_url, params={"query": query})
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise ImageAPIError(str(exc), original=exc)

    json_data = resp.json()

    if not isinstance(json_data, dict):
        raise ImageAPIError("Received malformed response from search API")

    search_results = tuple(
        ImageSearchResult(
            url=record.get("links", {}).get("download"),
            width=record.get("width"),
            height=record.get("height"),
        )
        for record in json_data.get("results", tuple())
    )

    return ImageSearchResultSet(search_results, json_data.get("total"))


@hookimpl
def search_backend():
    """
    Registers our Unsplash image API backend
    """
    return SearchBackendHook(
        name=PLUGIN_NAME,
        search=search,
        config_fields=CONFIG_FIELDS,
    )
