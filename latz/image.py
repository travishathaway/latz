from typing import NamedTuple, Literal

ImageTypes = Literal["png", "jpeg", "webp"]


class ImageSearchResult(NamedTuple):
    url: str
    image_type: ImageTypes
    description: str
    search_term: str


class ImageSearchResultSet(NamedTuple):
    results: tuple[ImageSearchResult, ...]
    number_results: int


def search(search_term: str) -> ImageSearchResultSet:
    """
    Find images based on a ``search_term`` and return an ``ImageSearchResultSet``
    """
    img_1 = ImageSearchResult(
        "https://travishathaway.com/image_1.png", "png", "test one", search_term
    )
    img_2 = ImageSearchResult(
        "https://travishathaway.com/image_2.jpg", "jpeg", "test two", search_term
    )

    return ImageSearchResultSet((img_1, img_2), 2)
