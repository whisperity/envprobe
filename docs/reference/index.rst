.. _impl_pypackage:

========================
Implementation reference
========================

Envprobe is implemented as a single Python package, named ``envprobe``.

.. warning::

    While we strive to make the code as modular and easily extensible as possible, at the core, Envprobe is a *single* program that is offered **whole**.
    The core functions that people use Envprobe for are not *fully* available if the Python package is used as a library, as some of the business logic is part of the command implementations; and as such, the below documentation is geared and intended more for people who would like to contribute to the tool, rather than people who would import it as a library.

.. toctree::

    shell/index
    vartypes/index
    environment
    settings/index


Miscellaneous functions
=======================

The :py:mod:`envprobe.library` module contains some miscellaneous functions that are used to tie the creation of the global objects accessing the environment and the user's state in a meaningful way.

.. currentmodule:: envprobe.library

.. autofunction:: get_shell_and_env_always
.. autofunction:: get_snapshot
.. autofunction:: get_variable_information_manager
.. autofunction:: get_variable_tracking
