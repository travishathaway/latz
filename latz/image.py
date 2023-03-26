from __future__ import annotations

from typing import NamedTuple


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
    search_backend: str
