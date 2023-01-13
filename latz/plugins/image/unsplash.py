from __future__ import annotations

import urllib.parse
from contextlib import contextmanager
from collections.abc import Iterator

from httpx import Client, Headers
from pydantic import BaseModel, Field

from ...image import (
    ImageSearchResult,
    ImageSearchResultSet,
)
from .. import hookimpl, ImageAPIPlugin

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


class UnsplashImageAPI:
    """
    Implementation of ImageAPI for use with the Unsplash API: https://unsplash.com/documentation
    """

    def __init__(self, client: Client):
        """Attach an `httpx.Client` object to our API"""
        self._client = client

    def search(self, query: str) -> ImageSearchResultSet:
        """
        Find images based on a ``search_term`` and return an ``ImageSearchResultSet``

        :raises HTTPError: Encountered during problems querying the API
        """
        search_url = urllib.parse.urljoin(BASE_URL, SEARCH_ENDPOINT)

        resp = self._client.get(search_url, params={"query": query})
        resp.raise_for_status()

        json_data = resp.json()

        search_results = tuple(
            ImageSearchResult(
                url=record.get("links", {}).get("download"),
                width=record.get("width"),
                height=record.get("height"),
            )
            for record in json_data.get("results", tuple())
        )

        return ImageSearchResultSet(search_results, json_data.get("total"))


@contextmanager
def unsplash_context_manager(config) -> Iterator[UnsplashImageAPI]:
    """
    Context manager that returns the ``UnsplashImageAPI`` we wish to use.
    This specific context manager handles setting up and tearing down the ``httpx.Client``
    connection that we use in this plugin.
    """
    client = Client()
    client.headers = Headers(
        {"Authorization": f"Client-ID {config.backend_settings.unsplash.access_key}"}
    )

    try:
        yield UnsplashImageAPI(client)
    finally:
        client.close()


@hookimpl
def image_api():
    """
    Registers our Unsplash image API backend
    """
    return ImageAPIPlugin(
        name=PLUGIN_NAME,
        image_api_context_manager=unsplash_context_manager,
        config_fields=CONFIG_FIELDS,
    )
