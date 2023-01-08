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

PLUGIN_NAME = "placeholder"


class PlaceholderBackendConfig(BaseModel):
    """
    Unsplash requires the usage of an ``access_key`` and ``secret_key``
    when using their API. We expose these settings here so users of the CLI
    tool can use it.
    """

    type: Literal["bear", "kitten"] = Field(
        default="kitten", description="The type of placeholder image links to use"
    )


CONFIG_FIELDS = {f"{PLUGIN_NAME}": (PlaceholderBackendConfig, {"type": "kitten"})}


class PlaceholderImageAPI(ImageAPI):
    """
    Used primarily to test and when we want to run the program without
    hitting any search endpoints.
    """

    def __init__(self, placeholder_type: str):
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


class PlaceholderImageAPIContextManager(ImageAPIContextManager):
    """
    Context manager for our PlaceholderImageAPI
    """

    def __enter__(self) -> PlaceholderImageAPI:
        return PlaceholderImageAPI(self._config.backend_settings.placeholder.type)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@hookimpl
def image_api():
    """
    Registers our Unsplash image API backend
    """
    return ImageAPIPlugin(
        name=PLUGIN_NAME,
        image_api_context_manager=PlaceholderImageAPIContextManager,
        config_fields=CONFIG_FIELDS,
    )
