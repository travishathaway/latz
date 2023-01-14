from typing import NamedTuple, Protocol

class ImageSearchResult(NamedTuple):
    url: Union[str, None]
    width: Union[int, None]
    height: Union[int, None]

class ImageSearchResultSet(NamedTuple):
    results: tuple[ImageSearchResult, ...]
    total_number_results: Union[int, None]

class ImageAPIContextManager(Protocol):
    def __enter__(self) -> ImageAPI: ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

class ImageAPI(Protocol):
    def search(self, query: str) -> ImageSearchResultSet: ...
