:mod:`rjgtoys.config` by Example
================================

A simple application
--------------------

Imagine a simple 'word translator' application: it accepts words on the command
line, looks up each word in a dictionary and prints the translation, if it has
one.

It reads the lookup dictionary from its configuration file.

Here is the code:

.. literalinclude:: ../../examples/translate.py

The class :class:`TranslateConfig` defines the configuration parameters needed
by the application.   The base class, :class:`~rjgtoys.config.Config` is based on :class:`pydantic.BaseModel`,
and should use type annotations to make the desired types clear, and to facilitate
validation of the input.

The :func:`~rjgtoys.config.getConfig` call returns an object that retrieves and provides access
to an instance of :class:`TranslateConfig` once a configuration file has been
chosen and read.

The ``cfg.add_arguments()`` call adds a ``--config`` command line option to the
application argument parser, which will set the location of the configuration file.
The same call also sets the default location for the configuration file, which in
this case is ``translate.yaml``, in the same directory as the ``translate.py`` script
itself.

To retrieve configuration parameters, simply access attributes of the configuration
object `cfg`, as if it were an instance of the specified configuration model,
:class:`TranslateConfig`.

Configuration file
------------------

Here is a suitable configuration file:

.. literalinclude:: ../../examples/english-french.yaml

If this file were stored in a file called `english-french.yaml` it would not be
found by default, and so to use it, the script should invoked as follows::

  $ python translate.py --config english-french.yaml cat dog budgie
  cat: chat
  dog: chien
  budgie: I don't know that word

Including defaults
------------------

One obvious way to make this dictionary available as the default would be to copy
or rename the file to ``translate.yaml``, but another way would be to make a new
``translate.yaml`` that uses the first as defaults::

  # examples/translate.yaml: Default configuration file, using specific dictionary
  defaults: !include english-french.yaml

The ``!include`` tag (a YAML tag provided by rjgtoys.yaml_) causes the
content of the named file to be inserted in
place of the tag, so the above is equivalent to::

  defaults:
    words:
       dog: chien
       cat: chat
       bird: oiseau

The configuration parser uses the `defaults` element of any mapping as a set of
initial values into which to merge any other values provided for that mapping.

In this case, there are no more keys, and so the above is equivalent to::

  words:
     dog: chien
     cat: chat
     bird: oiseau

Building on defaults
--------------------

However, the dictionary can also be extended::

  defaults: !include english-french.yaml

  words:
    snail: escargot

The above is equivalent to::

  words:
     dog: chien
     cat: chat
     bird: oiseau
     snail: escargot

.. _rjgtoys.yaml: https://rjgtoys.readthedocs.io/projects/yaml/en/latest/
