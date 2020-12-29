"""

Configuration sources
---------------------

These fetch data from configuration files.

.. autoclass:: ConfigSource

.. autoclass:: YamlFileConfigSource

.. autoclass:: SearchPathConfigSource

.. autoexception:: ConfigSearchFailed

"""

import os
from typing import List

from rjgtoys.xc import Error, Title

from rjgtoys.yaml import yaml_load_path


class ConfigSearchFailed(Error):
    """Raised when no configuration file could be found"""

    paths: List[str] = Title('List of paths that were searched')

    detail = "Configuration search failed, tried: {paths}"


class ConfigSource:
    """This is the base class for configuration sources, and is
    basically just an interface definition.

    It provides one method, :meth:`fetch` that should be
    overridden by subclasses to deliver data from some source.
    """

    # One day we'll need a pub-sub sort of interface
    # so a source can notify that it's been updated.
    # For now, this will do

    def fetch(self):
        """Fetches the current data from the source."""

        return {}


def resolve_noop(path):
    """The default 'resolve path' action; just returns the path it was given."""

    return path


class YamlFileConfigSource(ConfigSource):
    """This :class:`ConfigSource` implementation reads a configuration from
    a file containing YAML."""

    def __init__(self, path, resolve=None):
        """
        `path`
          The path to the file to be read.

        `resolve`
          If not `None`, is a callable that will be passed
          `path`, to allow it to be 'resolved' to an absolute pathname.
          The library function :func:`os.path.expanduser` would be a possible
          candidate.

        """

        super().__init__()
        self.path = path
        self.resolve = resolve or resolve_noop

    def fetch(self):

        path = self.resolve(self.path)

        data = yaml_load_path(path)
        return data


class SearchPathConfigSource(ConfigSource):
    """Searches a number of places for a configuration file."""

    DEFAULT_LOADER = YamlFileConfigSource

    def __init__(self, *paths, resolve=None, loader=None):
        """
        `paths`
          A list of paths to be tried, in order.

        `resolve`
          If not `None`, a callable that will be passed each
          path before it is tried, to allow it to 'resolve' the
          path into an absolute path.
          The library function :func:`os.path.expanduser` would be a possible
          candidate.

        `loader`
          The :class:`ConfigSource` implementation to use to try to
          load each possible path.   Must be a class or callable that
          can accept a single pathname parameter.  The default
          is ``self.DEFAULT_LOADER``, which is :class:`YamlFileConfigSource`.
        """

        self.loader = loader or self.DEFAULT_LOADER
        self.resolve = resolve or resolve_noop
        self.paths = [p for p in paths if p]

    def fetch(self):
        """Search for a readable file and return the data from it."""

        tries = []
        for p in self.paths:
            p = self.resolve(p)
            tries.append(p)
            if not os.path.exists(p):
#                print("SearchPathConfigSource did not find %s" % (p))
                continue
#            print("SearchPathConfigSource using %s" % (p))
            return self.loader(p).fetch()
        raise ConfigSearchFailed(paths=tries)

