from collections import Counter
from functools import reduce
from collections.abc import Callable

from click import ClickException
from pluggy import PluginManager  # type: ignore
from pydantic import create_model

from ..constants import APP_NAME
from ..config.models import BaseAppConfig
from ..image import ImageAPI
from .hookspec import AppHookSpecs
from .image import unsplash, placeholder


class AppPluginManager(PluginManager):
    """
    Our own custom subclass of PluginManager. We do this to add several convenience methods
    we use elsewhere in our application.
    """

    def __init__(self, *args, **kwargs):
        # We use this to cache the value of
        self.__image_api_names = None

        super().__init__(*args, **kwargs)

    def reset_cache(self) -> None:
        """Resets all cached properties"""
        self.__image_api_names = None

    @property
    def image_api_names(self) -> tuple[str, ...]:
        """
        Get the names of available image search apis that are currently configured.
        We cache this once per run.

        If there are duplicate names registered, we raise an exception.

        :raises ClickException: Raised if duplicate values are found (same plugin
                                is registered multiple times)
        """
        if self.__image_api_names is not None:
            return self.__image_api_names

        self.__image_api_names = tuple(
            image_search_api.name for image_search_api in self.hook.image_api()
        )
        names_counter = Counter(self.__image_api_names)
        duplicates = tuple(value for value, count in names_counter.items() if count > 1)

        if len(duplicates) > 0:
            raise ClickException(
                "Duplicate values for the following 'image_search_api' found: "
                f"{', '.join(duplicates)}"
            )

        return self.__image_api_names

    @property
    def image_api_config_fields(self) -> dict:
        """
        Returns all the registered config fields for the image_search_api plugins.
        We perform a merge of all registered ``config_fields`` dictionaries that represent
        the new configuration fields that will be added.

        TODO: add a duplicate check just like for API names
        """
        # Merge config fields from all registered plugins
        image_api_config = reduce(
            lambda dict_one, dict_two: {**dict_one, **dict_two},
            (
                image_search_api.config_fields
                for image_search_api in self.hook.image_api()
            ),
        )

        BackendSettings = create_model("BackendSettings", **image_api_config)

        return {"backend_settings": (BackendSettings, BackendSettings().dict())}

    def get_image_api_context_manager(self, app_config: BaseAppConfig) -> ImageAPI:
        """
        Gets the currently configured api_context_manager. This is a context manager
        that we can use to give us an ``ImageAPI`` object.

        :param app_config: Current app config object
        :raises ClickException: Raised if we cannot find an api_context_manager object to return
        """
        image_api_context_manager = None

        for api in self.hook.image_api():
            if api.name == app_config.backend:
                image_api_context_manager = api.image_api_context_manager

        if image_api_context_manager is None:
            raise ClickException(
                "Backend has been improperly configured. Please choose from the available"
                f" backends: {', '.join(self.image_api_names)}"
            )

        return image_api_context_manager

    def get_backend_validator_func(self) -> Callable:
        """Returns the validator function that is used by Pydantic when parsing configuration"""

        def validate_backend(cls, value):
            if value not in self.image_api_names:
                valid_names = ", ".join(self.image_api_names)
                raise ValueError(
                    f"'{value}' is not valid choice for backend. "
                    f"Available choices: {valid_names}"
                )
            return value

        return validate_backend


def get_plugin_manager() -> AppPluginManager:
    """
    Plugin manager for the application. This function registers all plugin
    hooks, internal and external plugins.
    """
    # This is the plugin manager object we return that the application will use
    # to get information about register plugins.
    plugin_manager = AppPluginManager(APP_NAME)

    # Adds plugin hooks
    plugin_manager.add_hookspecs(AppHookSpecs)

    # Registers internal plugin hooks
    plugin_manager.register(unsplash)
    plugin_manager.register(placeholder)

    # This is the magic that allows our application to discover other plugins
    # installed alongside it
    plugin_manager.load_setuptools_entrypoints(APP_NAME)

    return plugin_manager
