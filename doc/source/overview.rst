Overview
========

How the user sees configuration
-------------------------------

The user's view is of an application that accepts configuration parameters
in a file (or files) of YAML.

There are a number of standard, default places that the application looks for
the (primary) configuration file, and that search can be overridden or bypassed
by using a command-line option (`--config PATH`) to provide the path to the
primary configuration file.

Per-module configuration
------------------------

A application may be constructed from a number of components or packages, each
of which may require configuration parameters.

Each (Python) module that needs access to configuration data can declare a
data type (a class) that defines the parameters it needs.

That class definition is provided to the configuration system, which returns
an instance of that type, once the application has been configured.  (Actually
it returns a *proxy* to an instance, but that should not normally have
any impact on code that accesses the configuration object.)

The interface is modelled after the standard :mod:`logging`
interface.


User-controlled modular configuration
-------------------------------------

A single 'primary' configuration file is read by the application, and that
primary configuration file may reference other files, to include or merge
their content into the set of parameters provided to the application.

The inclusion mechanism provides the user and application builder with
a number of useful options:

1. A large set of parameters can be split into manageable chunks;

2. Multiple 'primary' configurations can reference the same 'secondary'
configuration files, to share common parameters, whilst differing on others;

3. To build sets of defaults that can be selectively overridden by user-provided
setting



Layered defaults
----------------

Configuration files can be 'layered', using one file to provide defaults
that may be overridden by others.

It is expected that the application itself will provide a default configuration
file that will be used by most users as their own set of defaults (i.e. will
be included as a 'base' for their own configuration).

This allows application designers to provide examples and options to users
in a simple and easily modifiable way, and allows users to create configurations
that state concisely only the differences between the user's desired configuration
and some other baseline configuration.

Configurable per-module views
-----------------------------

The components used in an application
may have been developed independently, and even if not, the
possibility that they might be used together in an application may not have been
anticipated by their designer(s).

The application configuration file must provide the parameters needed by all
its components, and should do so in a form that makes sense to its users.



Command line parser integration
-------------------------------

