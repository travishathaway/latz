from typing import Literal
from urllib.parse import urljoin

from pydantic import BaseModel, Field

from ...image import (
    ImageSearchResult,
    ImageSearchResultSet,
)
from .. import hookimpl, SearchBackendHook

#: Name of the plugin that will be referenced in our configuration
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


CONFIG_FIELDS = {PLUGIN_NAME: (PlaceholderBackendConfig, {"type": "kitten"})}


def search(client, config, query: str) -> ImageSearchResultSet:
    placeholder_type = config.backend_settings.placeholder.type
    base_url = f"https://place{placeholder_type}.com"
    sizes = ((200, 300), (600, 500), (1000, 800))

    results = tuple(
        ImageSearchResult(
            url=urljoin(base_url, f"{width}/{height}"),
            width=width,
            height=height,
        )
        for width, height in sizes
    )

    return ImageSearchResultSet(results=results, total_number_results=len(results))


@hookimpl
def image_api():
    """
    Registers our Unsplash image API backend
    """
    return SearchBackendHook(
        name=PLUGIN_NAME,
        search=search,
        config_fields=CONFIG_FIELDS,
    )
