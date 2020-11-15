"""
Tests for config sources.

"""

import os

from rjgtoys.config._config import Config, ConfigProxy
from rjgtoys.config._source import ConfigSearchFailed


from unittest.mock import sentinel

import pytest

def test_use_default_search():
    """If we do nothing, loading will use the default search path."""

    class MyConfig(Config):
        a: int = 3
        b: int = 2

    app_name = sentinel.app_name

    print("Using app_name %s" % (app_name))

    cfg = ConfigProxy(MyConfig)

    cfg.set_app_name(app_name)

    with pytest.raises(ConfigSearchFailed) as e:
        assert cfg.a == 3

    # The following has to track the ConfigManager.DEFAULT_SEARCH list

    expect_paths = [
        os.path.expanduser(p.format(app=app_name))
            for p in [
            './{app}.conf',
            '~/.{app}.conf',
            '~/.config/rjgtoys/{app}/{app}.conf',
            '~/.config/rjgtoys/{app}.conf',
            '/etc/{app}.conf'
            ]
    ]

    assert e.value.paths == expect_paths


