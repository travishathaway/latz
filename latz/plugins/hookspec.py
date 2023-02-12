from collections.abc import Iterable, Mapping
from typing import NamedTuple, Any, ContextManager
from collections.abc import Callable

import pluggy  # type: ignore
from pydantic import BaseModel

from latz.constants import APP_NAME
from latz.image import ImageAPI

hookspec = pluggy.HookspecMarker(APP_NAME)
hookimpl = pluggy.HookimplMarker(APP_NAME)

DefaultValues = Mapping[str, Any]
ConfigFields = Mapping[str, tuple[type[BaseModel], DefaultValues]]


class ImageAPIPlugin(NamedTuple):
    """
    Holds the metadata, config fields and context manager for the image search backend.

    Check out the [creating plugins][creating-plugins] for more information on writing
    plugins for latz.

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
        return ImageAPIPlugin(
            name="custom",
            ...
        )
    ```

    This would later be referred to as `custom` in the settings file:

    ```json
    {
      "backend": "custom",
      "backend_settings": {
        "custom": {
          "param_one": "value"
        }
      }
    }
    ```
    """

    image_api_context_manager: Callable[[Any], ContextManager[ImageAPI]]
    """
    Context manager for setting up and tearing down any connections as well returning
    an [`ImageAPI`][latz.image.ImageAPI] object to use for querying.

    **Example:**

    ```python
    from contextlib import contextmanager

    import httpx
    from latz.plugins import ImageAPIPlugin

    class CustomSearchAPI:
        ...

    @contextmanager
    def image_api_context_manager(config) -> Iterator[CustomSearchAPI]:
        client = httpx.Client()

        try:
            yield CustomSearchAPI(client)
        finally:
            client.close()

    @hookimpl
    def image_api():
        return ImageAPIPlugin(
            name="custom",
            image_api_context_manager=image_api_context_manager,
            ...
        )
    ```
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
    def image_api(self) -> Iterable[ImageAPIPlugin]:
        """
        Hookspec for the image API.

        Check out the [creating plugins][creating-plugins] guide for more information on
        using this plugin hook.
        """
        return tuple()  # default implementation returns no registered backends
