"""
This module implements the logic for interfacing with the environment's
contents, mapping variable primitives to internal data structure, keeping
state, etc.
"""
from copy import deepcopy
from enum import Enum
import os
import pickle

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
        self._elements = []

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


# Create the default type heuristic pipeline that only uses the default
# implementation.
default_heuristic = HeuristicStack()
default_heuristic += EnvVarTypeHeuristic()


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


class VariableDifferenceKind(Enum):
    UNKNOWN = 0
    CHANGED = 1
    REMOVED = 2
    ADDED = 3


class VariableDifference:
    """
    Represents and allows accessing the difference between the values of a
    variable.
    """
    def __init__(self, kind, var_name, old_value=None, new_value=None,
                 difference_actions=None):
        if not isinstance(kind, VariableDifferenceKind):
            raise TypeError("'kind' must be a valid kind")

        self.kind = kind
        self.variable = var_name
        self.old_value = old_value
        self.new_value = new_value
        self.diff_actions = difference_actions['diff'] if difference_actions \
            else []

    @property
    def is_simple_change(self):
        """
        :return: If the current difference only represents a simple change.

        A change is simple if it is either a single addition or delete, or
        a single definite change from one value to another.
        """
        return len(self.diff_actions) == 1 or \
            (len(self.diff_actions) == 2 and
                self.diff_actions[0][0] == '+' and
                self.diff_actions[1][0] == '-' and
                self.diff_actions[0][1] == self.new_value and
                self.diff_actions[1][1] == self.old_value)

    @property
    def is_new(self):
        """
        :return: If the current change sets the variable from an unset state
        to the set state.
        """
        return len(self.diff_actions) == 1 and not self.old_value

    @property
    def is_unset(self):
        """
        :return: If the current change unsets the variable from the previously
        set state.
        """
        return len(self.diff_actions) == 1 and not self.new_value


class Environment:
    """
    The Environment is responsible for owning and managing the understanding
    of environment variables in an environment.
    """
    def __init__(self, shell, env=None,
                 variable_type_heuristic=default_heuristic):
        """
        Initialises the environment manager for a particular :type:`Shell` and
        the set of key-value environment mappings.
        """
        self._shell = shell
        self._current_environment = deepcopy(env)
        self._stamped_environment = None
        self._type_heuristics = variable_type_heuristic

    def load(self):
        """
        Load the current shell's saved environment from storage into the memory
        as the :variable:`stamped_environment`.

        If there is no backing file associated with the current shell or a
        file access error happens, the stamped environment will be empty.
        """
        if not (self._shell.is_envprobe_capable and
                self._shell.manages_environment_variables):
            self._stamped_environment = {}
            return

        try:
            with open(self._shell.state_file, 'rb') as f:
                self._stamped_environment = pickle.load(f)
        except OSError:
            self._stamped_environment = {}

    def stamp(self):
        """
        Stamp the *current* environment passed to :func:`__init__` to store
        it in the :variable:`stamped_environment`.
        """
        # TODO: Please implement a better logic at stamping/saving, that only
        #       stamps (saves) the difference as already handled, not the
        #       ENTIRE shell.
        self._stamped_environment = deepcopy(self._current_environment)

    def save(self):
        """
        Emit the environment's *stamped* state
        (:variable:`stamped_environment`) to the storage for the current
        shell's backing file.

        If there is no backing file associated with the current shell, the
        method does nothing.
        """
        if not (self._shell.is_envprobe_capable and
                self._shell.manages_environment_variables):
            return

        with open(self._shell.state_file, 'wb') as f:
            pickle.dump(self._stamped_environment, f)
        os.chmod(self._shell.state_file, 0o0600)

    @property
    def current_environment(self):
        """
        Obtain the environment that was applicable to the running shell when
        the instance was constructed from the real world data.

        This represents the potentially "dirty" state which was read on the fly
        by Envprobe and could be changed by external factors.
        """
        return self._current_environment

    @property
    def stamped_environment(self):
        """
        Obtain the environment which was applicable at the last committed
        modification (such as calling of :func:`stamp()` or
        :func:`apply_change()`).

        This property represents the known state of the environment as was last
        time Envprobe destructively interacted with it.
        """
        if self._stamped_environment is None:
            self.load()
        return self._stamped_environment

    def apply_change(self, variable, remove=False):
        """
        Changes the variable in the :variable:`stamped_environment` have the
        value as passed in `variable`. If `remove` is `True`, the variable
        will be removed from memory.

        :note: This function does not change the representation as persisted
        in storage!
        """
        if not remove:
            self._stamped_environment[variable.name] = variable.to_raw_var()
        else:
            try:
                del self._stamped_environment[variable.name]
            except KeyError:
                pass

    def diff(self):
        """
        Calculate the difference between :variable:`stamped_environment` and
        :variable:`current_environment`.

        :return: A `dict` containing the :type:`VariableDifference` for each
        change.
        """
        diff = dict()

        def __create_difference(kind, var_name):
            old = create_environment_variable(var_name,
                                              self.stamped_environment,
                                              self._type_heuristics)
            new = create_environment_variable(var_name,
                                              self.current_environment,
                                              self._type_heuristics)

            if old is None or new is None:
                # If the saved (persisted) or the current environment does not
                # have the variable in it, it cannot or should not be
                # serialised anyways, so we ignore it.
                return

            if old.value != new.value:
                diff[var_name] = VariableDifference(
                        kind,
                        var_name,
                        old.value,
                        new.value,
                        type(old).get_difference(old, new))

        def __handle_elements(kind, iterable):
            for e in iter(iterable):
                __create_difference(kind, e)

        __handle_elements(
                VariableDifferenceKind.ADDED,
                set(self.current_environment.keys()) -
                set(self.stamped_environment.keys()))
        __handle_elements(
                VariableDifferenceKind.REMOVED,
                set(self.stamped_environment.keys()) -
                set(self.current_environment.keys()))
        __handle_elements(
                VariableDifferenceKind.CHANGED,
                set(self.current_environment.keys()) &
                set(self.stamped_environment.keys()))

        return diff
