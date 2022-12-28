from collections.abc import Iterable

import pluggy  # type: ignore

from ..constants import APP_NAME
from .types import ImageAPIPlugin

hookspec = pluggy.HookspecMarker(APP_NAME)
hookimpl = pluggy.HookimplMarker(APP_NAME)


class AppHookSpecs:
    """Holds all hookspecs for this application"""

    @hookspec
    def image_api(self) -> Iterable[ImageAPIPlugin]:
        """
        TODO: add example
        """
        return tuple()  # default implementation returns no registered backends
