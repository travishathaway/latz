from _typeshed import Incomplete
from collections.abc import Iterable
from latz.constants import APP_NAME as APP_NAME
from latz.image import ImageAPIContextManager as ImageAPIContextManager
from pydantic import BaseModel as BaseModel
from typing import Any, NamedTuple

hookspec: Incomplete
hookimpl: Incomplete

class ImageAPIPlugin(NamedTuple):
    name: str
    image_api_context_manager: type[ImageAPIContextManager]
    config_fields: dict[str, tuple[type[BaseModel], Any]]

class AppHookSpecs:
    def image_api(self) -> Iterable[ImageAPIPlugin]: ...
