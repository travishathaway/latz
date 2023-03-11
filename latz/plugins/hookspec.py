from collections.abc import Iterable, Mapping
from typing import NamedTuple, Any
from collections.abc import Callable

import httpx
import pluggy  # type: ignore
from pydantic import BaseModel

from latz.constants import APP_NAME
from latz.image import ImageSearchResultSet

hookspec = pluggy.HookspecMarker(APP_NAME)
hookimpl = pluggy.HookimplMarker(APP_NAME)

DefaultValues = Mapping[str, Any]
ConfigFields = Mapping[str, tuple[type[BaseModel], DefaultValues]]


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
    from latz.plugins import ImageAPIPlugin

    @hookimpl
    def image_api():
        return ImageSearchHook(
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

    search: Callable[[httpx.Client, Any, str], ImageSearchResultSet]
    """
    Callable that implements the search hook.
    """

    config_fields: ConfigFields
    """
    Mapping defining the namespace for the config parameters, the pydantic
    model to use and the default values it should contain.

    **Example:**

    ```python

    from pydantic import BaseModel, Field

    PLUGIN_NAME = "custom"

    class CustomConfigFields(BaseModel):
        access_key: str = Field(description="Access key for the API")

    CONFIG_FIELDS = {
        PLUGIN_NAME: (
            CustomConfigFields, {"access_key": ""}
        )
    }

    @hookimpl
    def image_api():
        return ImageAPIPlugin(
            name=PLUGIN_NAME,
            config_fields=CONFIG_FIELDS,
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
