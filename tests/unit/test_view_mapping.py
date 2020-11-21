"""
Tests for the view mapping machinery
"""

from unittest.mock import Mock

import json

import pytest

from rjgtoys.config import Config, ConfigProxy, ConfigManager

from rjgtoys.yaml import yaml_load

class ConfigModel(Config):

    a_int: int
    b_str: str


class StaticSource:
    """A config source that provides a literal."""

    def __init__(self, data):
        self._data = yaml_load(data)

    def fetch(self):
        return self._data


def test_view_map_default():
    """A default view map is applied correctly."""

    proxy = ConfigProxy(ConfigModel)

    ConfigManager.source = StaticSource("""
---
a_int: 2
b_str: "this is b"
    """)

    ConfigManager.load(always=True)

    v = proxy.value

    assert v.a_int == 2
    assert v.b_str == "this is b"


def test_view_map_local():
    """A locally defined view map is applied correctly."""

    proxy = ConfigProxy(ConfigModel, name='test.config.model')

    ConfigManager.source = StaticSource("""
---
my_a: 222
my_b: "remapped b"

a_int: 99
b_str: "If you see this or a_int==99, the test failed"

__view__:
   test.config.model:
     a_int: my_a
     b_str: my_b

    """)

    ConfigManager.load(always=True)

    v = proxy.value

    assert v.a_int == 222
    assert v.b_str == "remapped b"


def test_view_map_from_defaults():
    """A view map found in defaults is applied correctly."""

    proxy = ConfigProxy(ConfigModel, name='test.config.model')

    ConfigManager.source = StaticSource("""
---
my_a: 222
my_b: "remapped b"

a_int: 99
b_str: "If you see this or a_int==99, the test failed"

defaults:
  __view__:
     test.config.model:
       a_int: my_a
       b_str: my_b

    """)

    ConfigManager.load(always=True)

    v = proxy.value

    assert v.a_int == 222
    assert v.b_str == "remapped b"


def test_view_map_gets_default():
    """A view map found in defaults is applied correctly and gets data from defaults"""

    proxy = ConfigProxy(ConfigModel, name='test.config.model')

    ConfigManager.source = StaticSource("""
---
my_a: 222

a_int: 99
b_str: "If you see this or a_int==99, the test failed"

defaults:
  my_b: "remapped b"
  __view__:
     test.config.model:
       a_int: my_a
       b_str: my_b

    """)

    ConfigManager.load(always=True)

    v = proxy.value

    assert v.a_int == 222
    assert v.b_str == "remapped b"


def test_view_map_merges_views():
    """A view can be assembled from different mappings"""

    proxy = ConfigProxy(ConfigModel, name='test.config.model')

    ConfigManager.source = StaticSource("""
---
my_a: 222

a_int: 99
b_str: "If you see this or a_int==99, the test failed"

# At this level, we map to variables here (but my_b is missing)

__view__:
   test.config.model:
     a_int: my_a
     b_str: my_b

defaults:
  default_b: "defaulted b"

  # At this level, we map to variables at this level, but a is missing
  __view__:
     test.config.model:
       a_int: default_a
       b_str: default_b

    """)

    ConfigManager.load(always=True)

    # This is what it should look like when it's been mangled
    # - it went badly wrong during development so I'm keeping this
    # around just in case I break it again.

    assert ConfigManager.data == {
        "__view__": {
            "test.config.model": {
                "a_int": "my_a",
                "b_str": "my_b"
            }
        },
        "a_int": 99,
        "b_str": "If you see this or a_int==99, the test failed",
        "defaults": {
            "__view__": {
                "test.config.model": {
                    "a_int": "default_a",
                    "b_str": "default_b"
                }
            },
            "default_b": "defaulted b",
            "defaults": {}
        },
        "my_a": 222
    }

    v = proxy.value

    assert v.a_int == 222
    assert v.b_str == "defaulted b"



