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
        ...

    @abc.abstractmethod
    def get(self, image_id: str) -> ImageSearchResult:
        ...

    @abc.abstractmethod
    def download(self, image_id: str, path: Path) -> None:
        ...
