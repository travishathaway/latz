from typing import Literal
from urllib.parse import urljoin

from pydantic import BaseModel, Field

from ...image import (
    ImageSearchResult,
)
from .. import hookimpl, SearchBackendHook

#: Name of the plugin that will be referenced in our configuration
PLUGIN_NAME = "placeholder"


class PlaceholderBackendConfig(BaseModel):
    """
    Configuration for the placeholder backend. Currently only supports "bear"
    or "kitten".
    """

    type: Literal["bear", "kitten"] = Field(
        default="kitten", description="The type of placeholder image links to use"
    )


async def search(client, config, query: str) -> tuple[ImageSearchResult, ...]:
    """
    Search function for placeholder backend. It only returns three pre-defined
    search results. This is primarily meant for testing and demonstration purposes.
    """
    placeholder_type = config.search_backend_settings.placeholder.type
    base_url = f"https://place{placeholder_type}.com"
    sizes = ((200, 300), (600, 500), (1000, 800))

    return tuple(
        ImageSearchResult(
            url=urljoin(base_url, f"{width}/{height}"),
            width=width,
            height=height,
            search_backend=PLUGIN_NAME,
        )
        for width, height in sizes
    )


@hookimpl
def search_backend():
    """
    Registers our placeholder search backend
    """
    return SearchBackendHook(
        name=PLUGIN_NAME, search=search, config_fields=PlaceholderBackendConfig()
    )
