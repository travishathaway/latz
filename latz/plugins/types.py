from __future__ import annotations

from typing import NamedTuple, Any

from pydantic import BaseModel

from ..image import ImageAPI


class ImageAPIPlugin(NamedTuple):
    """
    Holds the metadata and class for the image search backend
    """

    name: str
    backend: type[ImageAPI]
    config_fields: dict[str, tuple[type[BaseModel], Any]]
