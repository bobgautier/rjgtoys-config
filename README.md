# `rjgtoys.config` - A modular configuration data interface

This package provides a simple and modular way for programs to access configuration
data.

The word 'modular' in the description refers to the way in which `rjgtoys.config`
allows independent modules or packages to define the structure of their configuration
data, whilst retrieving that data from a single combined source.

 * There is no need for a single, centralised definition of the 'config file format'
   for an application as a whole
 * An application can be built from packages and modules that use `rjgtoys.config`
   that are not aware of each other's configuration requirements
 * The structure of the configuration file is itself configurable; the components in
   an application do not impose it
