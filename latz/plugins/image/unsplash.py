from __future__ import annotations

import urllib.parse

from httpx import Client, Headers
from pydantic import BaseModel, Field

from ...image import (
    ImageAPI,
    ImageSearchResult,
    ImageSearchResultSet,
    ImageAPIContextManager,
)
from ..hookspec import hookimpl
from ..types import ImageAPIPlugin


PLUGIN_NAME = "unsplash"


class UnsplashBackendConfig(BaseModel):
    """
    Unsplash requires the usage of an ``access_key`` and ``secret_key``
    when using their API. We expose these settings here so users of the CLI
    tool can use it.
    """

    access_key: str = Field(description="Access key for the Unsplash API")

    secret_key: str = Field(description="Secret key for the Unsplash API")


CONFIG_FIELDS = {
    f"{PLUGIN_NAME}_config": (
        UnsplashBackendConfig,
        {"access_key": "", "secret_key": ""},
    )
}


class UnsplashImageAPI(ImageAPI):
    """
    Implementation of ImageAPI for use with the Unsplash API: https://unsplash.com/documentation
    """

    #: Base URL for the Unsplash API
    base_url = "https://api.unsplash.com/"

    #: Endpoint used for searching images
    search_endpoint = "/search/photos"

    def __init__(self, client_id: str, client: Client):
        """We use this initialization method to properly configure the ``httpx.Client`` object"""
        self._client_id = client_id
        self._headers = {"Authorization": f"Client-ID {client_id}"}
        self._client = client
        self._client.headers = Headers(self._headers)

    def search(self, query: str) -> ImageSearchResultSet:
        """
        Find images based on a ``search_term`` and return an ``ImageSearchResultSet``

        :raises HTTPError: Encountered during problems querying the API
        """
        search_url = urllib.parse.urljoin(self.base_url, self.search_endpoint)

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


class UnsplashImageAPIContextManager(ImageAPIContextManager):
    """
    Context manager that returns the ``UnsplashImageAPI`` we wish to use.
    This specific context manager handles setting up and tearing down the ``httpx.Client``
    connection that we use in this plugin.
    """

    def __enter__(self) -> UnsplashImageAPI:
        self.__client = Client()
        return UnsplashImageAPI(self._config.unsplash_config.access_key, self.__client)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__client.close()


@hookimpl
def image_api():
    """
    Registers our Unsplash image API backend
    """
    return ImageAPIPlugin(
        name=PLUGIN_NAME,
        image_api_context_manager=UnsplashImageAPIContextManager,
        config_fields=CONFIG_FIELDS,
    )
