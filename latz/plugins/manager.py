from pluggy import PluginManager  # type: ignore

from ..constants import APP_NAME
from .hookspec import AppHookSpecs
from .image import unsplash


def get_plugin_manager() -> PluginManager:
    """
    Plugin manager for the application. This function registers all plugin
    hooks, internal and external plugins.
    """
    # This is the plugin manager object we return that the application will use
    # to get information about register plugins.
    plugin_manager = PluginManager(APP_NAME)

    # Adds plugin hooks
    plugin_manager.add_hookspecs(AppHookSpecs)

    # Registers the internal plugin hook
    plugin_manager.register(unsplash)

    # This is the magic that allows our application to discover other plugins
    # installed alongside it
    plugin_manager.load_setuptools_entrypoints(APP_NAME)

    return plugin_manager
