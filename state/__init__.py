"""

"""
import os

from vartypes.string import StringEnvVar
from vartypes.path import PathLikeEnvVar


def create_environment_variable(key, env=os.environ):
    """
    Create an :type:`vartypes.EnvVar` instance for the given environment
    variable `key`.
    """

    # TODO: Improve this heuristic, introduce a way for the user to configure.
    if 'ENVPROBE' in key:
        # Don't allow the management of envprobe-specific variables.
        return None
    if 'PATH' in key:
        # Consider the variable a PATH-like variable.
        return PathLikeEnvVar(key, env.get(key, ""))
    else:
        return StringEnvVar(key, env.get(key, ""))
