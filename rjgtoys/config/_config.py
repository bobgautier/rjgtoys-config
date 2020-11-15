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

from typing import Optional, Callable

from pydantic import BaseModel

import weakref

from typing import List, Any

from rjgtoys.xc import Error, Title

from rjgtoys.config._yaml import yaml_load_path
from rjgtoys.config._source import YamlFileConfigSource, SearchPathConfigSource



class _ConfigAction(Action):
    """An :cls:`argparse.Action` that captures the configuration path provided on a command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        ConfigManager.set_path(values)


class ConfigUpdateError(Error):
    """Raised if there's a problem loading configuration values."""

    errors: List[Any] = Title("A list of (proxy, exception) pairs")

    detail = "There were error(s) loading the configuration: {errors}"


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

        cls.data = cls.source.fetch()

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


class ConfigProxy:
    """A 'proxy' for the configuration data needed by a client module.

    The proxy handles interaction with the source of configuration data
    and provides some handy methods without interfering with the 'purity'
    of the configuration data model itself.
    """

    manager_type = ConfigManager

    def __init__(self, model, manager_type=None):
        self._model = model
        self._modelname = "%s.%s" % (model.__module__, model.__qualname__)

        self._value = None

        self._manager = manager_type or self.manager_type

        self._manager.attach(self)

    def __str__(self):
        """Produce a helpful string representation."""

        return self._modelname

    __repr__ = __str__

    def update(self, data):
        """Called when new configuration data is available."""

        self._value = self._get_view(data, self._modelname, self._model)


    def _get_view(self, data, viewname, model):

        schema = model.schema()

        view = self._get_view_dict(data, viewname, schema)
        #print("_get_view %s is %s" % (viewname, view))
        return model(**view)

    def _get_view_dict(self, data, viewname, schema):

        # Do we have any defaults?

        defaults = resolve_defaults(data)

        #print("_get_view_dict data %s defaults %s" % (data, defaults))

        if defaults:
            data_defaults = self._get_view_dict(defaults, viewname, schema)
        else:
            data_defaults = {}

        view = self._get_view_mapping(data, viewname, schema)

        #print("Use view: %s" % (view))

        value = {}
        for n, k in view.items():
            try:
                value[n] = self._get_defaulted(data, k)
            except KeyError:
                pass

        return value

    def _get_view_mapping(self, data, viewname, schema):
        """Get the view mapping for viewname."""

        # Get the view mapping, if any
        # This is allowed to chase down defaults
        # if necessary

        try:
            view = self._get_defaulted(data, '__view__.%s' % (viewname))
        except KeyError:
            view = {}

        # Fill in any missing fields; those map directly to their names in the data

        view.update({ n: n for n in schema['properties'].keys() if n not in view })

        return view

    def _get_defaulted(self, data, item):
        """Get an item from data, using defaults if available."""

        missing = True
        try:
            value = self._getitem(data, item)
            missing = False
        except KeyError:
            pass

        # Try to return the default instead

        defaults = resolve_defaults(data)

        if not defaults:
            if missing:
                raise KeyError(item)
            return value

        try:
            default = self._get_defaulted(defaults, item)
            # If there was no explicit value, then the default
            # is the answer
            if missing:
                return default
        except KeyError:
            # No default.  If also no explicit value, we've no answer.
            # otherwise, use the explicit value.
            if missing:
                raise
            else:
                return value

        # Not missing, and there's a default.

        # If it's not a mapping, we return the explicit value

        if not isinstance(value, collections.abc.Mapping):
            return value

        # Override default from explicit, return the result

        config_merge(value, default)

        return default

    def _getitem(self, data, path):
        """Like getitem, but understands paths: m['a.b'] = m['a']['b']

        Also understands that some dicts have keys that contain dots.
        """

        try:
            return data[path]
        except KeyError:
            if '.' not in path:
                raise

        (p, q) = path.split('.',1)

        data = data[p]
        return self._getitem(data, q)

    def __getattr__(self, name):
        self._manager.load()
        return getattr(self._value, name)

    @property
    def value(self):
        self._manager.load()
        return self._value

    def add_arguments(self, parser, default=None, adjacent_to=None):

        # Get an 'application name' from the parser
        app_name = parser.prog.split('.',1)[0]

        self._manager.set_app_name(app_name)

        if adjacent_to:
            default = os.path.join(os.path.dirname(adjacent_to), default)

        # Use the default if none other can be found, or if none is specified

        self._manager.FALLBACK_PATH = default

        parser.add_argument(
            '--config',
            type=str,
            help="Path to configuration file",
            action=_ConfigAction,
            dest="_config_path"
        )

    def set_app_name(self, name):

        self._manager.set_app_name(name)

#
# Create a name for ConfigProxy that's reminiscent of
# logging.getLogger
#

getConfig = ConfigProxy


class Config(BaseModel):
    """A base class for configuration parameter objects.

    A convenient alias for :cls:`pydantic.BaseModel`.

    """

    # The following is an alternative to the getConfig()
    # function below.  I added it in the hope of avoiding
    # having too many things to import from rjgtoys.config
    # (you can just import the Config class, now) but on the
    # other hand it gets a bit mixed up with the pydantic
    # machinery; pydantic thinks the constructor takes
    # a proxy_type parameter.

    proxy_type: Optional[Callable] = ConfigProxy

    @classmethod
    def value(cls, other=None, proxy_type=None):

        other = other or cls

        proxy_type = proxy_type or other.proxy_type

        return proxy_type(other or cls)


def config_resolve(raw):
    """Resolve 'defaults' in some raw config data."""

    # If there are no defaults to apply, just return the raw data

    defaults = resolve_defaults(raw)
    if not defaults:
        return raw

    del raw['defaults']

    # override defaults with raw data, return result

    config_merge(raw, defaults)

    return defaults


def resolve_defaults(raw):
    """Resolve 'defaults' in some raw config data."""

    # If there are no defaults to apply, just return an empty dict

#    print("resolve_defaults %s" % (raw))

    try:
        defaults = raw['defaults']
    except KeyError:
        return {}

    # If only a single set of defaults, work around it

    if isinstance(defaults, collections.abc.Mapping):
        defaults = (defaults,)

    result = {}
    for layer in defaults:
        layer = config_resolve(layer)
        config_merge(layer, result)

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

