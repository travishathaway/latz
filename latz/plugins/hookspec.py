from collections.abc import Iterable
from typing import NamedTuple, Any

import pluggy  # type: ignore
from pydantic import BaseModel

from latz.constants import APP_NAME
from latz.image import ImageAPIContextManager

hookspec = pluggy.HookspecMarker(APP_NAME)
hookimpl = pluggy.HookimplMarker(APP_NAME)


class ImageAPIPlugin(NamedTuple):
    """
    Holds the metadata, config fields and context manager for the image search backend
    """

    name: str
    image_api_context_manager: type[ImageAPIContextManager]
    config_fields: dict[str, tuple[type[BaseModel], Any]]


class AppHookSpecs:
    """Holds all hookspecs for this application"""

    @hookspec
    def image_api(self) -> Iterable[ImageAPIPlugin]:
        """
        TODO: add example
        """
        return tuple()  # default implementation returns no registered backends
