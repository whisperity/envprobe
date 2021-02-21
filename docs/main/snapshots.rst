.. _snapshots:

===============
Saved snapshots
===============

.. Attention::

   This feature is yet to be implemented.

Variable tracking
=================

Saving certain environment variables (such as ``PWD``, ``SHLVL``, etc.) to a snapshot might not be beneficial.
The *tracking configuration* for variables can be used to toggle whether a particular variable (in the current shell, or globally for your user account) is useful to be saved, or not.
If a variable is *tracked*, changes to it are allowed to be saved and loaded from snapshots.
Otherwise, a variable is called *ignored*.
An *ignored* variable can still be :ref:`queried and modified<envvars>` through Envprobe for the current shell.

The tracking behaviour for any given variable is resolved in the following order:

 1. If the *local configuration* (for the current shell session) contains an explicit decision for the variable, that decision is used.
 2. If the *global configuration* (for your user account) contains an explicit decision for the variable, that decision is used.
 3. The local configuration's default setting is used.
 4. The global configuration's default setting is used.
 5. If there are no explicit nor default settings in either configuration files, the variables are *tracked*, by default.

The tracking of a variable can be changed by the :ref:`track<config_track>` configuration command.
