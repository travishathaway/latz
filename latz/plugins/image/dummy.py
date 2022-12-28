from typing import Literal
from urllib.parse import urljoin

from pydantic import BaseModel, Field

from ...image import (
    ImageAPI,
    ImageAPIContextManager,
    ImageSearchResult,
    ImageSearchResultSet,
)
from ..hookspec import hookimpl
from ..types import ImageAPIPlugin

PLUGIN_NAME = "dummy"

PlaceholderType = Literal["bear", "kitten"]


class DummyBackendConfig(BaseModel):
    """
    Unsplash requires the usage of an ``access_key`` and ``secret_key``
    when using their API. We expose these settings here so users of the CLI
    tool can use it.
    """

    placeholder_type: PlaceholderType = Field(
        default="kitten", description="The type of placeholder image links to use"
    )


CONFIG_FIELDS = {
    f"{PLUGIN_NAME}_config": (DummyBackendConfig, {"placeholder_type": "kitten"})
}


class DummyImageAPI(ImageAPI):
    """
    Used primarily to test and when we want to run the program without
    hitting any search endpoints.
    """

    def __init__(self, placeholder_type: PlaceholderType):
        self._placeholder_type = placeholder_type.lower()
        self._base_url = f"https://place{self._placeholder_type}.com"

    def search(self, query: str) -> ImageSearchResultSet:
        sizes = ((200, 300), (600, 500), (1000, 800))

        results = tuple(
            ImageSearchResult(
                url=urljoin(self._base_url, f"{width}/{height}"),
                width=width,
                height=height,
            )
            for width, height in sizes
        )

        return ImageSearchResultSet(results=results, total_number_results=len(results))


class DummyImageAPIContextManager(ImageAPIContextManager):
    """
    Dummy context manager for our DummyImageAPI
    """

    def __enter__(self) -> DummyImageAPI:
        return DummyImageAPI(self._config.dummy_config.placeholder_type)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@hookimpl
def image_api():
    """
    Registers our Unsplash image API backend
    """
    return ImageAPIPlugin(
        name=PLUGIN_NAME,
        image_api_context_manager=DummyImageAPIContextManager,
        config_fields=CONFIG_FIELDS,
    )
