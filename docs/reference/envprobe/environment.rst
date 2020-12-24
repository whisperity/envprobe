.. _impl_environment:

===========
Environment
===========

.. currentmodule:: envprobe.environment

.. autodata:: default_heuristic
   :no-value:
.. autofunction:: create_environment_variable

.. autoclass:: VariableDifferenceKind
.. autoclass:: VariableDifference

.. autoclass:: Environment
   :members:
   :special-members: __getitem__


Variable type heuristics
========================

.. autoclass:: EnvVarTypeHeuristic
   :members:
   :special-members: __call__

.. autoclass:: HeuristicStack
   :members:
   :special-members: __call__


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
