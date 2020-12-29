"""

.. autofunction:: getConfig

.. autoclass:: ConfigProxy
   :members: __getattr__,add_arguments

That's all there is to the main public interface; everything else
is either internals or hooks to allow exotic use cases, and I've yet to
document it.

"""

import os
from argparse import Action
import collections

from rjgtoys.config._manager import ConfigManager
from rjgtoys.config._ops import config_merge


class _ConfigAction(Action):
    """An :cls:`argparse.Action` that captures the configuration path provided on a command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        ConfigManager.set_path(values)



#
# Create an alias for ConfigProxy that's reminiscent of
# logging.getLogger - and make it a function so that
# Sphinx will document it as such
#

def getConfig(model,  name=None, manager_type=None):
    """Creates an object that can access configuration data.

    `model`
       The class describing the configuration data that is needed.
    `name`
       A name for the configuration data type; it defaults to a name
       derived from the module and class of `model`.
       This name is used to look up the view mapping for this configuration
       object.
    `manager_type`
       A class to manage configuration data.  Normally `None`, which
       means use the default, which is :class:`rjgtoys.config._manager.ConfigManager`.

    The returned value is a :class:`ConfigProxy`.

    """

    return ConfigProxy(model=model, name=name, manager_type=manager_type)


class ConfigProxy:
    """This class implements a 'proxy' for the configuration data needed by a client module,
    and is what you get back when you call :func:`getConfig`, although it
    tries hard to give the impression that you've actually got an instance of
    your declared configuration model class.

    A :class:`ConfigProxy` handles interaction with the source of configuration
    data and provides some handy methods without interfering with the 'purity'
    of the configuration data model itself.

    Refer to :func:`getConfig` for a description of the constructor parameters.

    """

    manager_type = ConfigManager

    def __init__(self, model, name=None, manager_type=None):
        self._model = model
        self._modelname = name or "%s.%s" % (model.__module__, model.__qualname__)

        self._value = None

        self._manager = manager_type or self.manager_type

        self._manager.attach(self)

    def __str__(self):
        """Produce a helpful string representation."""

        return self._modelname

    __repr__ = __str__

    def update(self, data):
        """Called (by a :class:`ConfigManager`) when new configuration data is available."""

        self._value = self._get_view(data, self._modelname, self._model)

    def _get_view(self, data, viewname, model):

        schema = model.schema()

        view = self._get_view_dict(data, viewname, schema)
        #print("_get_view %s is %s" % (viewname, view))
        return model(**view)

    def _get_view_dict(self, data, viewname, schema):

        # Do we have any defaults?

        defaults = data['defaults']

        #print("*** START ***")
        #print("_get_view_dict data %s defaults %s" % (data, defaults))

        #print("Get default view dict")
        if defaults:
            data_defaults = self._get_view_dict(defaults, viewname, schema)
        else:
            data_defaults = {}

        #print("Got default view dict")
        #print("data_defaults: %s" % (data_defaults,))

        view = self._get_view_mapping(data, viewname, schema)

        #print("Use view: %s" % (view))

        for n, k in view.items():
            try:
                data_defaults[n] = self._get_defaulted(data, k)
            except KeyError:
                pass

        return data_defaults

    def _get_view_mapping(self, data, viewname, schema):
        """Get the view mapping for viewname."""

        # Get the view mapping, if any
        # defaults have already been applied

        try:
            view = data['__view__'][viewname]
        except KeyError:
            view = {}

        # Fill in any missing fields; those map directly to their names in the data

        view.update({ n: n for n in schema['properties'].keys() if n not in view })

        #print("view_mapping(%s)" % (viewname))
        #print("data: %s" % (data))
        #print("view mapping: %s" % (view))

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

        defaults = data['defaults']

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
        # TODO?  Exception is default is not also a Mapping?

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
        """Attribute access to a :class:`ConfigProxy` is delegated to an
        instance of the configuration model class that it was constructed
        for, so the following accesses a `foo` attribute of an internal
        instance of `MyConfig`::

           cfg = getConfig(MyConfig)

           x = cfg.foo

        The proxy object ensures that configuration data has actually been
        loaded and parsed before returning the attribute value.
        """

        self._manager.load()
        return getattr(self._value, name)

    def add_arguments(self, parser, default=None, adjacent_to=None):
        """Adds a ``--config`` option to an :class:`argparse.ArgumentParser`.

        `parser`
          The :class:`argparse.ArgumentParser` to which to add the option.
        `default`
          The default configuration file to read.
        `adjacent_to`
          An optional path used to derive a directory path to use for
          relative configuration file paths.   For example if ``__file__`` is
          passed here, then a configuration file ``config.yaml`` would be searched
          for in the same directory as the calling module.

        Because this is a method of :class:`ConfigProxy`, and because instances
        of this class are returned from :func:`getConfig`, modules can usually do
        this::

            import argparse
            from rjgtoys.config import Config, getConfig

            class MyConfig(Config):
               name: str

            cfg = getConfig(MyConfig)

            parser = argparse.ArgumentParser()

            cfg.add_arguments(parser, default='myconfig.yaml')

            parser.add_argument('--name', type=str, help="Your name")

            args = parser.parse_args()

            name = args.name or cfg.name

            print(f"Hello, {name}!")

        Note:

          In the above, using `cfg.name` as the default for the
          ``--name`` parameter (`default=cfg.name` in the `add_arguments` call)
          won't work, because the configuration is not available until *after* the
          `parse_args()` call has returned.

        """

        # Get an 'application name' from the parser
        app_name = parser.prog.split('.',1)[0]

        self._manager.set_app_name(app_name)

        if adjacent_to and (default is not None):
            default = os.path.join(os.path.dirname(adjacent_to), default)

        # Use the default if none other can be found, or if none is specified

        self._manager.FALLBACK_PATH = default

        parser.add_argument(
            '--config',
            metavar="PATH",
            type=str,
            help="Path to configuration file",
            action=_ConfigAction,
            dest="_config_path"
        )

    def set_app_name(self, name):

        self._manager.set_app_name(name)

