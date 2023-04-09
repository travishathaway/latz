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
    search_backend: str | None
