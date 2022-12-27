from pathlib import Path

from pydantic import BaseModel, Field

from ...image import ImageAPI, ImageSearchResult, ImageSearchResultSet
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
    def __init__(self, client_id: str):
        self.client_id = client_id
        self._headers = {"Authorization": f"Client-ID {client_id}"}

    def search(self, search_term: str) -> ImageSearchResultSet:
        """
        Find images based on a ``search_term`` and return an ``ImageSearchResultSet``
        """
        img_1 = ImageSearchResult("https://travishathaway.com/image_1.png", "png")
        img_2 = ImageSearchResult("https://travishathaway.com/image_2.jpg", "jpeg")

        return ImageSearchResultSet((img_1, img_2), 2)

    def get(self, image_id: str) -> ImageSearchResult:
        return ImageSearchResult("https://travishathaway.com", "png")

    def download(self, image_id: str, path: Path) -> None:
        print("Downloading...")

    @classmethod
    def create(cls, config) -> "UnsplashImageAPI":
        """
        Factory method used to create this object by using values from the configuration object.
        """
        return cls(config.unsplash_config.access_key)


@hookimpl
def image_search_api():
    """
    Registers our Unsplash image API backend
    """
    return ImageAPIPlugin(
        name=PLUGIN_NAME, backend=UnsplashImageAPI, config_fields=CONFIG_FIELDS
    )
