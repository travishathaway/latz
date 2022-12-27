from pathlib import Path

from pydantic import BaseModel, Field

from ...image import ImageAPI, ImageSearchResult, ImageSearchResultSet
from ..hookspec import hookimpl
from ..types import ImageAPIPlugin


class UnsplashBackendConfig(BaseModel):
    """"""

    access_key: str = Field(description="Access for the Unsplash API")
    secret_key: str = Field(description="Secret for the Unsplash API")


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
        print("Downloading")


@hookimpl
def image_search_api():
    """
    Registers our Unsplash image API backend
    """
    return ImageAPIPlugin(
        name="unsplash", backend=UnsplashImageAPI, config=UnsplashBackendConfig
    )
