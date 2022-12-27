import abc
from typing import Literal, NamedTuple
from pathlib import Path


ImageTypes = Literal["png", "jpeg", "webp"]


class ImageSearchResult(NamedTuple):
    url: str
    description: str


class ImageSearchResultSet(NamedTuple):
    results: tuple[ImageSearchResult, ...]
    number_results: int


class ImageAPI(abc.ABC):
    """
    Abstract base class for the Image API
    """

    @abc.abstractmethod
    def search(self, search_term: str) -> ImageSearchResultSet:
        """
        Used to search for an image via a search term and then return a single result set
        """

    @abc.abstractmethod
    def get(self, image_id: str) -> ImageSearchResult:
        """
        Used to get metadata about an image given with a unique identifier.
        """

    @abc.abstractmethod
    def download(self, image_id: str, path: Path) -> None:
        """
        Used to download images to a local computer.
        """

    @classmethod
    @abc.abstractmethod
    def create(cls, config) -> "ImageAPI":
        """
        Use this as a factory function for creating new classes with values from the application
        configuration.
        """
