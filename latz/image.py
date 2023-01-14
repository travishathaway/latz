from __future__ import annotations

from typing import NamedTuple, Protocol


class ImageSearchResult(NamedTuple):
    """
    Represents an individual search result object. It holds all relevant data
    for a single search result including the image size and URL.
    """
    url: str | None
    width: int | None
    height: int | None


class ImageSearchResultSet(NamedTuple):
    """
    Represents a result set of [`ImageSearchResult`][latz.image.ImageSearchResult] objects.
    This is the object that must be returned on the `search` method of classes implementing
    the [`ImageAPI`][latz.image.ImageAPI] protocol.
    """
    results: tuple[ImageSearchResult, ...]
    total_number_results: int | None


class ImageAPIContextManager(Protocol):
    """
    Protocol class used to help plugin authors create compatible context managers.

    In latz, we rely on context managers to perform setup and tear-down operations
    for the connections t

    We use a class-based approach here to make sure that plugin authors appropriately
    implement the type of context manager the application needs (i.e. one that returns
    an implementation of [`ImageAPI`][latz.image.ImageAPI]).
    """

    def __enter__(self) -> ImageAPI:
        """
        This must return an implementation of the below [`ImageAPI`][latz.image.ImageAPI] class
        """

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Used to ensure the context manager protocol has been implemented"""


class ImageAPI(Protocol):
    """
    Protocol class for the image API plugin. This is used to make sure that
    objects being returned implement at least the methods defined below with the appropriate
    return types.
    """

    def search(self, query: str) -> ImageSearchResultSet:
        """
        Used to search for an image via a search term and then return a single result set.
        See [`ImageSearchResultSet`][latz.image.ImageSearchResultSet] for more information
        about the return type.
        """
