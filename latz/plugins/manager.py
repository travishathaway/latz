from collections import Counter
from functools import reduce

from click import ClickException
from pluggy import PluginManager  # type: ignore

from ..constants import APP_NAME
from ..config.models import BaseAppConfig
from ..image import ImageAPI
from .hookspec import AppHookSpecs
from .image import unsplash


class AppPluginManager(PluginManager):
    """
    Our own custom subclass of PluginManager. We do this to add several convenience methods
    we use elsewhere in our application.
    """

    def __init__(self, *args, **kwargs):
        # We use this to cache the value of
        self.__image_search_api_names = None

        super().__init__(*args, **kwargs)

    def reset_cache(self) -> None:
        """Resets all cached properties"""
        self.__image_search_api_names = None

    @property
    def image_search_api_names(self) -> tuple[str, ...]:
        """
        Get the names of available image search apis that are currently configured.
        We cache this once per run.

        If there are duplicate names registered, we raise an exception.

        :raises ClickException: Raised if duplicate values are found (same plugin
                                is registered multiple times)
        """
        if self.__image_search_api_names is not None:
            return self.__image_search_api_names

        self.__image_search_api_names = tuple(
            image_search_api.name for image_search_api in self.hook.image_search_api()
        )
        names_counter = Counter(self.__image_search_api_names)
        duplicates = tuple(value for value, count in names_counter.items() if count > 1)

        if len(duplicates) > 0:
            raise ClickException(
                "Duplicate values for the following 'image_search_api' found: "
                f"{', '.join(duplicates)}"
            )

        return self.__image_search_api_names

    @property
    def image_search_api_config_fields(self) -> dict:
        """
        Returns all the registered config fields for the image_search_api plugins.
        We perform a merge of all registered ``config_fields`` dictionaries that represent
        the new configuration fields that will be added.

        TODO: add a duplicate check just like for API names
        """
        return reduce(
            lambda dict_one, dict_two: {**dict_one, **dict_two},
            (
                image_search_api.config_fields
                for image_search_api in self.hook.image_search_api()
            ),
        )

    def get_current_image_search_api(self, app_config: BaseAppConfig) -> ImageAPI:
        """
        Gets the currently configured ImageAPI class based on the passed in ``app_config``
        object.

        :param app_config: Current app config object
        :raises ClickException: Raised if we cannot find an ImageAPI object to return
        """
        image_search_api = None

        for search_api in self.hook.image_search_api():
            if search_api.name == app_config.backend:
                image_search_api = search_api.backend.create(app_config)

        if image_search_api is None:
            raise ClickException(
                "Backend has been improperly configure. Please choose from the available"
                f" backends: {','.join(self.image_search_api_names)}"
            )

        return image_search_api


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

    # Registers the internal plugin hook
    plugin_manager.register(unsplash)

    # This is the magic that allows our application to discover other plugins
    # installed alongside it
    plugin_manager.load_setuptools_entrypoints(APP_NAME)

    return plugin_manager
