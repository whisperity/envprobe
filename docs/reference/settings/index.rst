.. _impl_settings:

===========================
Handling user configuration
===========================

The :py:mod:`envprobe.settings` package implements classes that deal with handling configuration that is specific to the user, or a particular shell.

.. toctree::

   snapshot
   variable_tracking


Abstract configuration files
============================

.. currentmodule:: envprobe.settings.config_file

The :py:class:`ConfigurationFile` class allows accessing a *key-value mapping* (:py:class:`dict`) of configuration objects that is saved to the user's file system to a `JSON <http://json.org>`_ file.

.. autoclass:: ConfigurationFile
   :members:
   :special-members: __len__, __contains__, __iter__, __getitem__, __setitem__, __delitem__, __enter__, __exit__

