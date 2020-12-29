"""

.. autoclass:: Config

"""


from pydantic import BaseModel


class Config(BaseModel):
    """This is the base class for configuration parameter objects.

    It is little more than a convenient alias for :class:`pydantic.BaseModel`.

    To define your own configuration parameter structure, you should
    create a subclass and define attributes of whatever types you need.

    This class contains an internal :class:`Config` class which provides
    configuration parameters to Pydantic.  The parameter `arbitrary_types_allowed`
    is set `True` (see arbitrary_types_allowed_ in the Pydantic documentation
    for a full description)

.. _arbitrary_types_allowed: https://pydantic-docs.helpmanual.io/usage/types/#arbitrary-types-allowed

    Amy module that requires configuration data should declare a subclass
    to contain the necessary data, and then call :func:`rjgtoys.config.getConfig`
    on it to return a suitable proxy::

        from rjgtoys.config import Config, getConfig

        class MyConfig(Config):
           name: str

        cfg = getConfig(MyConfig)

        print(f"Hello, {cfg.name}!")

    """

    class Config:
        """Tell pydantic to allow arbitrary attribute types."""

        arbitrary_types_allowed = True
