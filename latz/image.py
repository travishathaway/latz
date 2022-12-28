from __future__ import annotations

import abc
from typing import Literal, NamedTuple


ImageTypes = Literal["png", "jpeg", "webp"]


class ImageSearchResult(NamedTuple):
    url: str | None
    width: int | None
    height: int | None


class ImageSearchResultSet(NamedTuple):
    results: tuple[ImageSearchResult, ...]
    total_number_results: int | None


class ImageAPIContextManager(abc.ABC):
    """
    Used to help plugin authors create compliant context managers.

    We use a class-based approach here to make sure that plugin authors appropriately
    implement the type of context manager the application needs (i.e. one that returns
    an implementation of ``ImageAPI``).
    """

    def __init__(self, config) -> None:
        """Used to initialize and configure the ``ImageAPI`` object"""
        self._config = config

    @abc.abstractmethod
    def __enter__(self) -> ImageAPI:
        """This must return an implementation of the below ``ImageAPI`` class"""

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Used to ensure the context manager protocol has been implemented"""


class ImageAPI(abc.ABC):
    """
    Abstract base class for the Image API
    """
    @abc.abstractmethod
    def search(self, query: str) -> ImageSearchResultSet:
        """
        Used to search for an image via a search term and then return a single result set
        """
