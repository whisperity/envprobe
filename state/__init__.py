"""

"""
import os

from configuration import variable_types
from vartypes import ENVTYPE_NAMES_TO_CLASSES
from vartypes.numeric import NumericEnvVar
from vartypes.path import PathLikeEnvVar
from vartypes.string import StringEnvVar


__all__ = ['environment', 'saved', 'create_environment_variable']


def create_environment_variable(key, env=None):
    """
    Create an :type:`vartypes.EnvVar` instance for the given environment
    variable `key`.
    """
    if not env:
        env = os.environ

    if 'ENVPROBE' in key:
        # Don't allow the management of Envprobe-specific variables, under
        # no circumstance.
        return None

    # The type that will be constructed...
    clazz = None

    # The user's preference overrides other heuristics.
    with variable_types.VariableTypeMap(read_only=True) as type_map:
        if key in type_map:
            clazz = ENVTYPE_NAMES_TO_CLASSES[type_map[key]]

    if clazz is None:
        if 'PATH' in key:
            clazz = PathLikeEnvVar
        elif key.startswith('_'):
            # By default consider variables that begin with _ "hidden" and
            # un-managed.
            clazz = None
        else:
            try:
                # Try converting the result to a number.
                value = env.get(key, None)
                if value is not None:
                    value = float(value)
                    value = int(value)

                    # If successful, a numeric type could be used.
                    clazz = NumericEnvVar
            except (TypeError, ValueError):
                # If all else fails, a string env var could always work.
                clazz = StringEnvVar

    return clazz(key, env.get(key, "")) if clazz else None
