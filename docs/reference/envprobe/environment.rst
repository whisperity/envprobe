.. _impl_environment:

======================
Environment management
======================

.. currentmodule:: envprobe.environment

The :py:mod:`envprobe.environment` module implements the logic that allow Envprobe to keep track of the current environment it is running in.
At the core of the library is the :py:class:`.Environment` class, which is instantiated together with the current :py:class:`.shell.Shell`.

.. autofunction:: create_environment_variable

.. autoclass:: Environment(shell, env, variable_type_heuristics)
   :members:
   :special-members: __getitem__


Difference of environments
==========================

The :py:func:`environment.diff` function returns for each variable instances of the following class.

.. autoclass:: VariableDifference
   :members:

.. autoclass:: VariableDifferenceKind

   .. autoattribute:: ADDED
      :no-value:

   .. autoattribute:: CHANGED
      :no-value:

   .. autoattribute:: REMOVED
      :no-value:


Type heuristics
===============

To ensure that environment variables (which are in almost all cases handled simply as strings until they are parsed by a program) can be :ref:`managed in a type-safe manner<impl_vartypes>`, heuristics that map a raw environment variable to a proper type can be passed to :py:func:`create_environment_variable` and :py:class:`Environment`.

.. autoclass:: EnvVarTypeHeuristic
   :members:
   :special-members: __call__

.. autoclass:: HeuristicStack
   :members:
   :special-members: __call__

.. autodata:: default_heuristic
   :no-value:

Available heuristics
--------------------

The following heuristics are implemented in the :py:mod:`vartype_heuristics` module.
All these classes are subclasses of :py:class:`EnvVarTypeHeuristic<envprobe.environment.EnvVarTypeHeuristic>`.

.. currentmodule:: envprobe.vartype_heuristics
.. autosummary::
   :nosignatures:

   EnvprobeEnvVarHeuristic
   HiddenEnvVarHeuristic
   PathEnvVarHeuristic
   NumericalNameEnvVarHeuristic
   NumericalValueEnvVarHeuristic

.. autodata:: standard_vartype_pipeline
   :no-value:
