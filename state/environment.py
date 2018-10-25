"""
Handles managing the saved state of a shell environment.
"""
import copy
import os
import pickle
from enum import Enum

from . import create_environment_variable


class VariableDifferenceType(Enum):
    UNKNOWN = 0
    CHANGED = 1
    REMOVED = 2
    ADDED = 3


class VariableDifference():
    """
    Indicates a difference in a variable's value.
    """
    def __init__(self, type, variable_name,
                 old_value=None, new_value=None,
                 difference_actions=None):
        if not isinstance(type, VariableDifferenceType):
            raise ValueError("'type' must be the enum type "
                             "'VariableDifferenceType'.")

        self.type = type
        self.variable = variable_name
        self.old_value = old_value
        self.new_value = new_value
        self.differences = difference_actions['diff'] \
            if difference_actions else []

    def dict(self):
        return {"type": self.type.name,
                "variable": self.variable,
                "old": self.old_value,
                "new": self.new_value,
                "diffs": self.differences}


class Environment():
    """
    This class is used for managing the environment variables' state in a
    loaded shell.
    """
    def __init__(self, shell):
        self._shell = shell
        self._current_env = dict(copy.deepcopy(os.environ))
        self._saved_env = None

        if self._shell.is_envprobe_capable():
            self.load()

    def save(self):
        """
        Save the current environment stored in the local instance to the
        shell's state file.
        """
        if not self._shell.is_envprobe_capable():
            return

        with open(self._shell.state_file, 'wb') as f:
            pickle.dump(self._current_env, f)

        self._saved_env = dict(copy.deepcopy(self._current_env))

    def load(self):
        """
        Load the registered current shell's environment into the "saved_env"
        variable. This does not affect the "current_env".
        """
        if not self._shell.is_envprobe_capable():
            return

        try:
            with open(self._shell.state_file, 'rb') as f:
                self._saved_env = pickle.load(f)
        except OSError:
            # If the file cannot be opened, just skip behaviour.
            pass

    @property
    def saved_env(self):
        """
        Obtain the environment that was applicable to the shell when the last
        save() was called.
        """
        return self._saved_env

    @property
    def current_env(self):
        """
        Obtain the environment which is currently applicable in the shell.
        """
        return self._current_env

    def diff(self):
        """
        Calculate and get the difference between saved_env() and
        current_env().

        :return: A dict containing the :type:`state.VariableDifference` for
        each variable that has been changed.
        """
        diff = dict()

        def __create_difference(diff_type, key):
            old = create_environment_variable(key, self.saved_env)
            new = create_environment_variable(key, self.current_env)

            if not old or not new:
                # If the old or new environment variable doesn't have a
                # value property, it cannot or should not be serialised,
                # thus we ignore it.
                return

            if old.value != new.value:
                diff[key] = VariableDifference(
                    diff_type, key, old.value, new.value,
                    type(old).get_difference(old, new))

        def __handle_keys(type, iterable):
            for key in iter(iterable):
                __create_difference(type, key)

        __handle_keys(
            VariableDifferenceType.ADDED,
            set(self.current_env.keys()) - set(self.saved_env.keys()))

        __handle_keys(
            VariableDifferenceType.REMOVED,
            set(self.saved_env.keys()) - set(self.current_env.keys()))

        __handle_keys(
            VariableDifferenceType.CHANGED,
            set(self.saved_env.keys()) & set(self.current_env.keys()))

        return diff
