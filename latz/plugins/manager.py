from __future__ import annotations

from collections import Counter
from functools import reduce
from collections.abc import Callable

from pluggy import PluginManager  # type: ignore
from pydantic import create_model

from ..constants import APP_NAME
from ..exceptions import LatzError
from .hookspec import AppHookSpecs, SearchBackendHook
from .image import unsplash, placeholder

#: Name of the dynamically generated pydantic model for search backend settings.
#: These settings are registered via plugins.
SEARCH_BACKEND_SETTINGS_MODEL = "SearchBackendSettings"

#: Key used in the configuration of the dynamically generated settings from plugins.
SEARCH_BACKEND_SETTINGS_KEY = "search_backend_settings"


class AppPluginManager(PluginManager):
    """
    Our own custom subclass of PluginManager. We do this to add several convenience methods
    we use elsewhere in our application.
    """

    def __init__(self, *args, **kwargs):
        # This is used as a cache
        self.__search_backend_hooks = None

        super().__init__(*args, **kwargs)

    def reset_cache(self) -> None:
        """Resets all cached properties"""
        self.__search_backend_hooks = None

    @property
    def search_backend_names(self) -> tuple[str, ...]:
        """
        Get the names of available search backends that are currently configured.
        We cache this once per run.

        If there are duplicate names registered, we raise an exception.

        :raises LatzError: Raised if duplicate values are found (same plugin
                                is registered multiple times)
        """
        if self.__search_backend_hooks is not None:
            return self.__search_backend_hooks

        self.__search_backend_hooks = tuple(
            search_backend.name for search_backend in self.hook.search_backend()
        )
        names_counter = Counter(self.__search_backend_hooks)
        duplicates = tuple(value for value, count in names_counter.items() if count > 1)

        if len(duplicates) > 0:
            raise LatzError(
                "Duplicate values for the hook 'search_backend' found: "
                f"{', '.join(duplicates)}. Please make sure to define a unique 'name' field"
            )

        return self.__search_backend_hooks

    def get_configured_search_backends(self, config) -> tuple[SearchBackendHook, ...]:
        """
        Get the search backends that are currently configured to be used.
        These are differently than those that have simply been registered.
        """
        return tuple(
            search_backend
            for search_backend in self.hook.search_backend()
            if search_backend.name in config.search_backends
        )

    @property
    def search_backend_config_fields(self) -> dict:
        """
        Returns all the registered config fields for the `search_backend` plugins.
        We perform a merge of all registered `config_fields` dictionaries that represent
        the new configuration fields that will be added.

        TODO: add a duplicate check just like for search backend names
        """
        # Merge config fields from all registered plugins
        search_backend_config = reduce(
            lambda dict_one, dict_two: {**dict_one, **dict_two},
            (
                {search_backends.name: search_backends.config_fields}
                for search_backends in self.hook.search_backend()
            ),
        )

        SearchBackendSettings = create_model(
            SEARCH_BACKEND_SETTINGS_MODEL, **search_backend_config
        )

        return {
            SEARCH_BACKEND_SETTINGS_KEY: (
                SearchBackendSettings,
                SearchBackendSettings().dict(),
            )
        }

    def get_backend_validator_func(self) -> Callable:
        """Returns the validator function that is used by Pydantic when parsing configuration"""

        def validate_backend(cls, values):
            for value in values:
                if value not in self.search_backend_names:
                    valid_names = ", ".join(self.search_backend_names)
                    raise ValueError(
                        f"'{value}' is not a valid choice for a search backend. "
                        f"Available choices: {valid_names}"
                    )
            return values

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
