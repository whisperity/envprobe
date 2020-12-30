.. _impl_pypackage:

==============
Python package
==============

Envprobe is implemented as a single Python package, named ``envprobe``.

.. warning::

   While we strive to make the code as modular and easily extensible as possible, at the core, Envprobe is a *single* program that is offered **whole**.
   The core functions that people use Envprobe for are not available if the Python package is used as a library, and as such, the below documentation is geared and intended more for people who would like to contribute to the tool, rather than people who would import it as a library.

.. toctree::
   :maxdepth: 1

   shell/index
   vartypes/index
   environment
   settings/index


Miscellaneous functions
=======================

.. currentmodule:: envprobe.library

.. autofunction:: get_shell_and_env_always
