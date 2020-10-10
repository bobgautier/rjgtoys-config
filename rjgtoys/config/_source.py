"""

Configuration sources

"""

import os
from typing import List

from rjgtoys.xc import Error, Title

from ._yaml import yaml_load_path


class ConfigSearchFailed(Error):

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
    """'Resolve' a path by doing nothing to it."""

    return path


class YamlFileConfigSource(ConfigSource):

    def __init__(self, path, resolve=None):
        super().__init__()
        self.path = path
        self.resolve = resolve or resolve_noop

    def fetch(self):

        path = self.resolve(self.path)

        data = yaml_load_path(path)

        return data


class SearchPathConfigSource(ConfigSource):

    def __init__(self, *paths, resolve=None, loader=None):
        self.loader = loader or YamlFileConfigSource
        self.resolve = resolve or resolve_noop
        self.paths = paths

    def fetch(self):
        tries = []
        for p in self.paths:
            p = self.resolve(p)
            tries.append(p)
            if not os.path.exists(p):
                continue
            return self.loader(p).fetch()
        raise ConfigSearchFailed(paths=tries)


