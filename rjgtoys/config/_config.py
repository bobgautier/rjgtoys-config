"""

Configuration data management.

Provide modules with access to 'configuration' data.

That data often comes from a 'configuration file' that is loaded
at application startup time.

The configuration data provides parameters that are inconvenient to
specify in other ways and which need to be varied relatively infrequently.


"""

import sys
import os

import collections

from argparse import Action

from pydantic import BaseModel

import weakref

from typing import List, Any

from rjgtoys.xc import Error, Title

from ._yaml import yaml_load_path
from ._source import YamlFileConfigSource, SearchPathConfigSource


class Config(BaseModel):
    """A convenient alias for :cls:`pydantic.BaseModel`."""

    pass


class _ConfigAction(Action):
    """An :cls:`argparse.Action` that captures the configuration path provided on a command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        ConfigManager.set_path(values)


class ConfigUpdateError(Error):
    """Raised if there's a problem loading configuration values."""

    errors: List[Any] = Title("A list of (proxy, exception) pairs")

    detail = "There were error(s) loading the configuration"


def default_app_name():
    """Generate a default application name."""

    # Try to use the script name

    name = os.path.basename(sys.argv[0]).split('.',1)[0]

    # Not sure what else to try!

    return name



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
        '/etc/{app}.conf'
        ]

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

        paths = [p.format(app=cls.app_name) for p in paths]

        cls.source = SearchPathConfigSource(*paths, resolve=cls._resolve_path)
        cls.loaded = False

    @classmethod
    def _resolve_path(cls, path):
        return os.path.expanduser(path.format(app=cls.app_name))

    @classmethod
    def set_app_name(cls, name):
        cls.app_name = name

    @classmethod
    def load(cls):
        """Ensure the data is loaded."""

        if cls.loaded:
            return

        if cls.source is None:
            print("Using default search %s" % (cls.DEFAULT_SEARCH))
            cls.source = SearchPathConfigSource(
                *cls.DEFAULT_SEARCH,
                resolve=cls._resolve_path
            )

        data = cls.source.fetch()

        cls.data = config_resolve(data)

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
                errors.append((p, e))

        # Report any errors

        if errors:
            raise ConfigUpdateError(errors)

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


class ConfigProxy:
    """A 'proxy' for the configuration data needed by a client module.

    The proxy handles interaction with the source of configuration data
    and provides some handy methods without interfering with the 'purity'
    of the configuration data model itself.
    """

    def __init__(self, model):
        self._model = model
        self._modelname = "%s.%s" % (model.__module__, model.__qualname__)

        self._value = None

        ConfigManager.attach(self)

    def update(self, data):
        """Called when new configuration data is available."""

        self._value = self._get_view(data, self._modelname, self._model)

    def _get_view(self, data, viewname, model):
        """Build a view of the data, and use it to instantiate 'model'."""

        view = data.get('__view__')
        if view is not None:
            view = view.get(viewname)
        if view is None:
            # build a default view

            schema = model.schema()
            view = { n: n for n in schema['properties'].keys() }

        value = {}
        for n, k in view.items():
            try:
                value[n] = self._getitem(data, k)
            except KeyError:
                pass

        return model(**value)

    @staticmethod
    def _getitem(data, path):
        """Like getitem, but understands paths: m['a.b'] = m['a']['b'] """

        for p in path.split('.'):
            data = data[p]

        return data

    def __getattr__(self, name):
        ConfigManager.load()
        return getattr(self._value, name)

    @property
    def value(self):
        return self._value

    def add_arguments(self, parser, default=None):

        # Get an 'application name' from the parser
        app_name = parser.prog.split('.',1)[0]

        ConfigManager.set_app_name(app_name)
        ConfigManager.set_path(default)

        parser.add_argument(
            '--config',
            type=str,
            help="Path to configuration file",
            action=_ConfigAction,
            dest="_config_path",
            default=default
        )

    def set_app_name(self, name):

        ConfigManager.set_app_name(name)

def getConfig(cls):
    """Return a 'config' object that can fetch configuration data."""

    return ConfigProxy(cls)


def config_resolve(raw):
    """Resolve 'defaults' in some raw config data."""

    # If there are no defaults to apply, just return the raw data

    try:
        defaults = raw['defaults']
    except KeyError:
        return raw

    result = {}
    for layer in defaults:
        layer = config_resolve(layer)
        config_merge(layer, result)

    del raw['defaults']

    config_merge(raw, result)

    return result


def config_merge(part, result):
    """Merge a set of defaults 'part' into 'result'."""

    for (key, value) in part.items():
        # If value is a mapping, any
        # existing value in result had better
        # be a mapping too.
        # Merge the mappings.
        # Otherwise, just override
        if not isinstance(value, collections.abc.Mapping):
            result[key] = value
            continue

        # See if there's an existing value

        try:
            prev = result[key]
        except KeyError:
            # No, just override
            result[key] = value
            continue

        # Merge prev and new

        config_merge(value, prev)

