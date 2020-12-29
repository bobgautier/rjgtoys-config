rjgtoys.config: A modular configuration data interface
======================================================

This package provides a simple and modular way for programs to access configuration
data.

The word 'modular' in the description refers to the way in which `rjgtoys.config`
allows independent modules or packages to define the structure of their configuration
data, whilst retrieving that data from a single combined source.

 * There is no need for a single, centralised definition of the 'config file format'
   for an application as a whole
 * An application can be built from packages and modules that use `rjgtoys.config`
   without having to be 'aware' of each other's config requirements
 * The structure of the config file is itself configurable; the components in
   an application do not impose it

About this documentation
------------------------

I'm struggling to get the structure of the documentation right for this package.

There is an attempt at an 'overview', in which I avoid too much technical detail
(but the result is far to abstract and vague).

Then there are two separate attempts at 'tutorial'-style walkthroughs, which cover
very similar ground in slightly different ways.  And neither is complete.

.. toctree::
   :maxdepth: 2

   overview
   example
   tutorial
   reference
   getting
   todo




