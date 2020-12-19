"""
This module implements the logic for interfacing with the environment's
contents, mapping variable primitives to internal data structure, keeping
state, etc.
"""
from . import vartypes


class EnvVarTypeHeuristic:
    """
    This class and its subclasses implement heuristics that define how an
    environment variable is mapped to a particular type.
    """
    def __call__(self, name, env=None):
        """
        The default implementation for a heuristic is simply to consider
        everything a string variable.

        In derived classes, the implementation should return the names of the
        var type implementation, or `None` if the heuristic doesn't return
        anything.
        If the implementation deduces that the given variable should not be
        manageable by Envprobe, `False` should be returned.
        """
        return 'string'


class HeuristicStack:
    """
    Implements a simple stack that resolves an environment variable's type
    by calling each heuristic until an answer is reached.
    """
    def __init__(self):
        self._elements = list()

    def __add__(self, heuristic):
        self._elements.append(heuristic)
        return self

    def __call__(self, name, env=None):
        for h in reversed(self._elements):
            result = h(name, env)
            if result:
                return result
            if result is False:
                break
        return None


def create_environment_variable(name, env, pipeline):
    """
    Creates an :type:`envprobe.vartypes.EnvVar` instance for the environment
    variable given in `name` in the environment map `env`.

    :param:`pipeline` is used to figure out the type of the environment
    variable to instantiate.
    """
    kind = pipeline(name, env)
    if not kind:
        raise KeyError("Couldn't resolve '%s' to a variable type." % name)

    clazz = vartypes.load(kind)
    return clazz(name, env.get(name, ""))


# Let's define some "standard" heuristics.
class EnvprobeEnvVarHeuristic(EnvVarTypeHeuristic):
    """
    This heuristic disables accessing the 'ENVPROBE_' variables, which are
    needed to be exact to allow Envprobe to run.
    """
    def __call__(self, name, env=None):
        if name.startswith("ENVPROBE_"):
            return False


class HiddenEnvVarHeuristic(EnvVarTypeHeuristic):
    """
    Consider environment variables that begin with a _ as hidden ones that
    should not be managed.
    """
    def __call__(self, name, env=None):
        if name.startswith('_'):
            return False


class PathEnvVarHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        if name == "PATH" or name.endswith("PATH"):
            return 'path'


class NumericalNameEnvVarHeuristic(EnvVarTypeHeuristic):
    """
    This heuristic maps commonly number-only named variables to the numeric
    type.
    """
    def __call__(self, name, env=None):
        if name.endswith(("PID", "PORT")):
            return 'numeric'


class NumericalValueEnvVarHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        if not env:
            return None

        value = env.get(name, "")
        try:
            float(value)
            return 'numeric'
        except ValueError:
            return None
