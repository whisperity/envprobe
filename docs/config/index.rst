.. _config:

============================================
Settings and configuration (``config`` mode)
============================================

Envprobe's settings entry point is called the ``config`` mode, which is responsible for allowing you to tweak how Envprobe behaves.

If Envprobe is properly :ref:`installed<install_hook>`, the shell will have the ``envprobe-config`` command, and its shorthand alias, ``epc``, defined.
Calling ``epc`` automatically brings up the argument parser for *config mode*.

.. attention::

   The list of available subcommands for a mode is generated in a *context-sensitive* fashion.
   This means that in case the current context does not allow the execution of an action, Envprobe will usually fail with an ``invalid choice`` error.

.. toctree::
   :maxdepth: 2

   hook
