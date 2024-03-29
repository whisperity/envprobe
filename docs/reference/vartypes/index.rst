.. _impl_vartypes:

==========================
Environment variable types
==========================

The :py:mod:`envprobe.vartypes` package implements the logic that maps different environment variables allows Envprobe to interface with system shells.

.. currentmodule:: envprobe.vartypes
.. autoclass:: EnvVar
    :members:

The extended information for an environment variable is stored in objects of the following class.

.. currentmodule:: envprobe.vartypes.envvar
.. autoclass:: EnvVarExtendedInformation
    :members:

.. _impl_vartypes_implemented_list:

Implemented types
=================

The list of known variable types in Envprobe are documented in the pages
accessible from the links below.

.. currentmodule:: envprobe.vartypes
.. autosummary::
    :toctree: generated
    :nosignatures:

    string.String
    numeric.Numeric
    array.Array
    colon_separated.ColonSeparatedArray
    semi_separated.SemicolonSeparatedArray
    path.Path

Dynamic loading
===============

The library is designed to be dynamically loading the individual environment variable type implementations.
This is accomplished by the following functions, used extensively in clients of the library.

.. currentmodule:: envprobe.vartypes
.. autofunction:: get_class
.. autofunction:: get_kind
.. autofunction:: get_known_kinds
.. autofunction:: load
.. autofunction:: load_all


Registering implementations
---------------------------

.. currentmodule:: envprobe.vartypes
.. autofunction:: register_type
