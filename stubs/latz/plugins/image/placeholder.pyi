from .. import ImageAPIPlugin as ImageAPIPlugin, hookimpl as hookimpl
from ...image import ImageSearchResult as ImageSearchResult, ImageSearchResultSet as ImageSearchResultSet
from _typeshed import Incomplete
from collections.abc import Generator
from pydantic import BaseModel
from typing import Literal

PLUGIN_NAME: str

class PlaceholderBackendConfig(BaseModel):
    type: Literal['bear', 'kitten']

CONFIG_FIELDS: Incomplete

class PlaceholderImageAPI:
    def __init__(self, placeholder_type: str) -> None: ...
    def search(self, query: str) -> ImageSearchResultSet: ...

def placeholder_context_manager(config) -> Generator[Incomplete, None, None]: ...
def image_api(): ...
