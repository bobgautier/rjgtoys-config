"""
Tests for the view mapping machinery
"""

from unittest.mock import Mock

from rjgtoys.config import Config, ConfigProxy, ConfigManager

from rjgtoys.config.yaml import yaml_load

class ConfigModel(Config):

    a_int: int
    b_str: str


def test_view_map_default():
    """A default view map is applied correctly."""

    proxy = ConfigProxy(ConfigModel)

    config_data = yaml_load("""
---
a_int: 2
b_str: "this is b"
    """)

    src = Mock()
    src.fetch = Mock(return_value=config_data)

    ConfigManager.source = src

    ConfigManager.load()

    v = proxy.value

    assert v.a_int == 2
    assert v.b_str == "this is b"


