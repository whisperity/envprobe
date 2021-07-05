.. _impl_shell:

===============
Shell interface
===============

The :py:mod:`envprobe.shell` package implements the logic that allows Envprobe to interface with system shells.

.. currentmodule:: envprobe.shell

.. autoclass:: CapabilityError
.. autofunction:: get_current_shell
.. autoclass:: Shell
    :members:


Dynamic loading
===============

The *Shell* library is designed to be dynamically loading the individual shell implementations.
This is accomplished by the following functions, used extensively in clients of the library.

.. autofunction:: get_class
.. autofunction:: get_kind
.. autofunction:: get_known_kinds
.. autofunction:: load
.. autofunction:: load_all


Registering implementations
---------------------------

.. autofunction:: register_type
