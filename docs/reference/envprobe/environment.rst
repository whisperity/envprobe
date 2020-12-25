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

Foo

.. autoclass:: VariableDifferenceKind
.. autoclass:: VariableDifference

Type heuristics
===============

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

The following heuristics are implemented in the `environment` module.
All these classes are subclasses of :py:class:`EnvVarTypeHeuristic<envprobe.environment.EnvVarTypeHeuristic>`

.. autosummary::
   :nosignatures:

   EnvprobeEnvVarHeuristic
   HiddenEnvVarHeuristic
   PathEnvVarHeuristic
   NumericalNameEnvVarHeuristic
   NumericalValueEnvVarHeuristic
