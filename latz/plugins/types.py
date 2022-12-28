from __future__ import annotations

from typing import NamedTuple, Any

from pydantic import BaseModel

from ..image import ImageAPIContextManager


class ImageAPIPlugin(NamedTuple):
    """
    Holds the metadata and class for the image search backend
    """

    name: str
    image_api_context_manager: type[ImageAPIContextManager]
    config_fields: dict[str, tuple[type[BaseModel], Any]]
