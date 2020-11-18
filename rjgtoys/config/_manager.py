

import os
import sys

from typing import List, Any

import weakref

from rjgtoys.xc import Error, Title

from rjgtoys.config._source import YamlFileConfigSource, SearchPathConfigSource
from rjgtoys.config._ops import config_normalise


def default_app_name():
    """Generate a default application name."""

    # Try to use the script name

    name = os.path.basename(sys.argv[0]).split('.',1)[0]

    # Not sure what else to try!

    return name


class ConfigUpdateError(Error):
    """Raised if there's a problem loading configuration values."""

    errors: List[Any] = Title("A list of (proxy, exception) pairs")

    detail = "There were error(s) loading the configuration: {errors}"



class ConfigManager:
    """The central manager for configuration data.

    This is essentially a singleton implemented as a
    class with class methods.

    It handles remembering where to get configuration from,
    and holding the data.

    It also provides a registry of :cls:`_ConfigProxy` objects
    that are interfaces to (parts of) the configuration data
    from client modules.

    """

    # The application name that will be inserted into config paths as {app}

    app_name = default_app_name()

    # The configuration source; if necessary a None will be replaced by
    # a search path (see DEFAULT SEARCH below)

    source = None

    # Has the data been loaded?

    loaded = False

    # If so, this is the data

    data = None

    # List of registered proxies that need to be notified when data is loaded

    proxies = []

    # Default list of places to search

    DEFAULT_SEARCH = [
        './{app}.conf',
        '~/.{app}.conf',
        '~/.config/rjgtoys/{app}/{app}.conf',
        '~/.config/rjgtoys/{app}.conf',
        '/etc/{app}.conf'
        ]

    FALLBACK_PATH = None

    @classmethod
    def get_search_env(cls):
        return dict(app=cls.app_name)

    @classmethod
    def set_path(cls, path):
        """Set the path for a subsequent load.

        Remember that we've not yet loaded this data.
        """

        if path is None:
            return

        cls.source = YamlFileConfigSource(path, resolve=cls._resolve_path)
        cls.loaded = False

    @classmethod
    def set_search(cls, *paths):
        """Set search path for a subsequent load."""

        if not paths:
            return

        cls.source = SearchPathConfigSource(*paths, resolve=cls._resolve_path)
        cls.loaded = False

    @classmethod
    def _resolve_path(cls, path):
        env = cls.get_search_env()
        return os.path.expanduser(path.format(**env))

    @classmethod
    def set_app_name(cls, name):
        cls.app_name = name

    @classmethod
    def load(cls):
        """Ensure the data is loaded."""

        if cls.loaded:
            return

        if cls.source is None:
#            print("Using default search %s" % (cls.DEFAULT_SEARCH))
            cls.source = SearchPathConfigSource(
                *cls.DEFAULT_SEARCH,
                cls.FALLBACK_PATH,
                resolve=cls._resolve_path
            )

        data = cls.source.fetch()

        cls.data = config_normalise(data)

        cls.loaded = True

        # Figure out which proxies are still live, and update them

        live_proxies = []
        real_proxies = []
        for w in cls.proxies:
            p = w()
            if p is None:
                continue
            real_proxies.append(p)
            live_proxies.append(w)

        cls.proxies = live_proxies

        errors = []
        for p in real_proxies:
            try:
                p.update(cls.data)
            except Exception as e:
                #raise
                errors.append((p, e))

        # Report any errors

        if errors:
            raise ConfigUpdateError(errors=errors)

    @classmethod
    def attach(cls, proxy):
        """Register a proxy."""

        cls.proxies.append(weakref.ref(proxy))

        # If we already have data, update the new proxy
        # (because it missed being called when we loaded)

        if cls.loaded:
            try:
                proxy.update(cls.data)
            except Exception as e:
                raise ConfigUpdateError([(proxy, e)])

