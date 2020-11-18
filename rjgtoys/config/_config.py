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

from typing import Optional, Callable

from pydantic import BaseModel


from rjgtoys.xc import Error, Title

from rjgtoys.config._proxy import ConfigProxy
from rjgtoys.config.thing import Thing
from rjgtoys.config.yaml import yaml_load_path


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

