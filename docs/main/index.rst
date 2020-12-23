.. _main:

===============================================
Environment variable management (``main`` mode)
===============================================

Envprobe's main entry point is called the ``main`` mode, which is responsible for managing environment variables.
This is the mode that is interfaced with most of the time.

If Envprobe is properly :ref:`installed<install_hook>`, the shell will have the ``envprobe`` command, and its shorthand alias, ``ep``, defined.
Calling ``ep`` automatically brings up the argument parser for *main mode*.

The ``main`` mode is also unique in offering *shortcuts* to further lessen the amount of typing needed to interface with the tool.

.. toctree::
   :maxdepth: 2

   envvars
   saves
