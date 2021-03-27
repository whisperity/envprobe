.. _index:

========
Envprobe
========

**Envprobe** (``envprobe``) is a shell hook tool that helps you manage your environment variables on a per-shell basis easily.
It allows for doing so without requiring typing in clunky ``export`` sequences, or manually ``source``-ing who-knows-where hand-written script files.


Audience
========

Envprobe is provided for power users of Unix-derivative systems, especially for software developers.
If your day-to-day life on your computer does not involve juggling shell configuration, you will not find much use of this tool.


Comparison to existing tools
============================

Envprobe was conceived to be the tool between some already existing ones that allow managing your environment.

- Scripts can be evaluated in a running shell with ``source``.
  This is a cumbersome operation, as the scripts need to be maintained, especially when one is still writing the initial version.
- `Shell Modules <http://modules.sourceforge.net>`_ (``module load``) allow loading pre-installed versions of software and apply their environment configuration to the local shell.
  These *modulefiles* are to be written usually by package maintainers and are distributed with the installed tools and allow the user to dynamically load or unload the "availability" of a tool.
- `direnv <http://direnv.net>`_ loads and applies the ``export`` directives (specified in the ``.envrc`` files) in the context of the current directory, and its parents.

Envprobe provides the environment variable modification experience inside the current shell, with no need of manually writing configuration files.
You can change your environments on the fly and if the setup works, Envprobe can save the configuration for you, and load it later.


Documentation
=============

.. toctree::

   install
   quick
   main/index
   config/index
   reference/index


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
