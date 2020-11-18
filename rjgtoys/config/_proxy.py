
from argparse import Action
import collections

from rjgtoys.config._manager import ConfigManager
from rjgtoys.config._ops import config_merge


class _ConfigAction(Action):
    """An :cls:`argparse.Action` that captures the configuration path provided on a command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        ConfigManager.set_path(values)


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

        defaults = data['defaults']

        #print("_get_view_dict data %s defaults %s" % (data, defaults))

        if defaults:
            data_defaults = self._get_view_dict(defaults, viewname, schema)
        else:
            data_defaults = {}

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

