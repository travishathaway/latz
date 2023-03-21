from collections.abc import Iterable, Awaitable
from typing import NamedTuple, Any
from collections.abc import Callable

import httpx
import pluggy  # type: ignore
from pydantic import BaseModel

from latz.constants import APP_NAME
from latz.image import ImageSearchResultSet

hookspec = pluggy.HookspecMarker(APP_NAME)
hookimpl = pluggy.HookimplMarker(APP_NAME)


class SearchBackendHook(NamedTuple):
    """
    Holds the metadata and callable for using the image search hook.
    """

    name: str
    """
    Namespace for the image API plugin; this is the value users will use in their
    config files to specify this particular plugin.

    **Example:**

    ```python
    from latz.plugins import SearchBackendHook

    @hookimpl
    def search_backend():
        return SearchBackendHook(
            name="custom",
            ...
        )
    ```

    This would later be referred to as `custom` in the settings file:

    ```json
    {
      "search_backends": ["custom"],
      "search_backend_settings": {
        "custom": {
          "param_one": "value"
        }
      }
    }
    ```
    """

    search: Callable[[httpx.AsyncClient, Any, str], Awaitable[ImageSearchResultSet]]
    """
    Callable that implements the search hook.
    """

    config_fields: BaseModel
    """
    Mapping defining the namespace for the config parameters, the pydantic
    model to use and the default values it should contain.

    **Example:**

    ```python

    from pydantic import BaseModel, Field

    PLUGIN_NAME = "custom"

    class CustomConfigFields(BaseModel):
        access_key: str = Field(description="Access key for the API")

    @hookimpl
    def image_api():
        return ImageAPIPlugin(
            name=PLUGIN_NAME,
            config_fields=CustomConfigFields(access_key=""),
            ...
        )
    ```
    """


class AppHookSpecs:
    """Holds all hookspecs for this application"""

    @hookspec
    def search_backend(self) -> Iterable[SearchBackendHook]:
        """
        Hookspec for the search backend hook.

        Check out the [creating plugins][creating-plugins] guide for more information on
        using this plugin hook.
        """
        return tuple()
