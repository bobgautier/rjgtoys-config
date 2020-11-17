"""

Configuration sources

"""

import os
from typing import List

from rjgtoys.xc import Error, Title

from rjgtoys.config.yaml import yaml_load_path


class ConfigSearchFailed(Error):
    """Raised when no configuration file could be found"""

    paths: List[str] = Title('List of paths that were searched')

    detail = "Configuration search failed, tried: {paths}"


class ConfigSource:

    # One day we'll need a pub-sub sort of interface
    # so a source can notify that it's been updated.
    # For now, this will do

    def fetch(self):
        """Fetch current data."""

        return {}


def resolve_noop(path):
    """The default 'resolve path' action; just returns the path it was given."""

    return path


class YamlFileConfigSource(ConfigSource):
    """Reads a configuration from YAML."""

    def __init__(self, path, resolve=None):
        super().__init__()
        self.path = path
        self.resolve = resolve or resolve_noop

    def fetch(self):

        path = self.resolve(self.path)

        data = yaml_load_path(path)

        return data


class SearchPathConfigSource(ConfigSource):
    """Searches a number of places for a configuration file."""

    def __init__(self, *paths, resolve=None, loader=None):
        self.loader = loader or YamlFileConfigSource
        self.resolve = resolve or resolve_noop
        self.paths = [p for p in paths if p]

    def fetch(self):
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

