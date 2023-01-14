from .. import ImageAPIPlugin as ImageAPIPlugin, hookimpl as hookimpl
from ...image import ImageSearchResult as ImageSearchResult, ImageSearchResultSet as ImageSearchResultSet
from _typeshed import Incomplete
from collections.abc import Iterator
from httpx import Client
from pydantic import BaseModel

PLUGIN_NAME: str

class UnsplashBackendConfig(BaseModel):
    access_key: str

CONFIG_FIELDS: Incomplete
BASE_URL: str
SEARCH_ENDPOINT: str

class UnsplashImageAPI:
    def __init__(self, client: Client) -> None: ...
    def search(self, query: str) -> ImageSearchResultSet: ...

def unsplash_context_manager(config) -> Iterator[UnsplashImageAPI]: ...
def image_api(): ...
