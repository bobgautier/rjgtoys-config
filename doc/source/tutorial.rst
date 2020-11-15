Tutorial
========

Overview
--------

In order to use :mod:`rjgtoys.config` in your package, you need to:

1. Decide what configuration parameters you need, and design a structure to represent them;
2. Ideally, write a default YAML configuration file that sets sensible default values;
3. Define your configuration parameter structure in Python.
4. Implement a little 'glue code' in the top of your package.

Background: Pydantic
--------------------

`rjgtoys.config` is built on Pydantic_, a package that builds on the Python type annotation
mechanism to implement type-checked data classes.


.. _Pydantic: https://pydantic-docs.helpmanual.io/


Step One: define your configuration parameters
----------------------------------------------

In your package, define a class based on :class:`rjgtoys.config.Config` that
represents the configuration parameters that you need.

The configuration file will be in YAML, so it's capable of representing structured
objects, lists, and so on, so don't feel constrained to make the configuration object
just a simple list of named attributes.

You need to think about how the YAML will look, because that's the 'user interface'
to your configuration mechanism.

The class you define is a :class:`pydantic.BaseModel` subclass and so you are
expected to use type annotations and any other pydantic machinery to add validation
to the data.

For example, imagine you are writing a mailshot tool: it will send an email
to a number of recipients, specified as a 'mailing list name'.   The mailing
lists are defined in a configuration file that we'd like to look like this::

  # Mailing list configuration
  ---
  target_lists:
    list1:
      - bob@somewhere.com
      - alice@elsewhere.com
    list2:
      - friend@faraway.planet.mars
      - buddy@moon.biz

The object to receive this might look like this::

  from typing import Dict, List
  from rjgtoys.config import Config

  # Step One: declare configuration parameters

  class MailerConfig(Config):

    target_lists: Dict[str, List[str]]

Step Two: connect your code to the configuration system
-------------------------------------------------------

Create an object that will receive the configuration parameters.

This is essentially just boilerplate code, and it usually goes
at the top of the module, after the configuration class has been
defined::

  from typing import Dict, List
  from rjgtoys.config import Config, getConfig

  # Step One: declare configuration parameters

  class MailerConfig(Config):

    target_lists: Dict[str, List[str]]

  # Step Two: connect to the configuration system

  cfg = getConfig(MailerConfig)

Step Three: Use the data
------------------------

To use the configuration parameters in your code, you just reference
attributes of the ``cfg`` object as if it were an instance of
your configuration class (it isn't)::


  from typing import Dict, List
  from rjgtoys.config import Config, getConfig

  # Step One: declare configuration parameters

  class MailerConfig(Config):

    target_lists: Dict[str, List[str]]

  # Step Two: connect to the configuration system

  cfg = getConfig(MailerConfig)

  # Step Three: use the data

  def get_recipients(list_name):
      """Returns the list of members of a mailing list."""

      return cfg.target_lists[list_name]

Step Four: Allow the user to override the default
-------------------------------------------------

Your application needs a way to locate a configuration file.

You will normally provide a default path (or search path),
along with a way to override that default.

If you use the standard :mod:`argparse` command line parser,
:mod:`rjgtoys.config` can help with that.

While you are building your applications's :class:`argparse.ArgumentParser`
call ``cfg.add_arguments()`` to add a ``--config`` option, and specify
a default configuration file.

Then, once you've parsed the command line, the configuration can be used::

  def main(argv=None):
     parser = argparse.ArgumentParser('Send a message to a mailing list')

     parser.add_argument('--list', type=str, help="Name of the list")

     cfg.add_arguments(parser, default='mailer.conf', adjacent_to=__file__)

     args = parser.parse_args(argv)

     print(f"Mail will be sent to mailing list {args.list}:")

     for member in get_recipients(args.list):
         print(f"   {member}")

