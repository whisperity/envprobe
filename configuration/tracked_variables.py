"""
Handles managing the user's own ("global") and the current shell's ("local")
preference on what variables' value change should be tracked by Envprobe.
"""
import os

from . import get_configuration_folder
from .locking_configuration_json import LockingConfigurationJSON


class TrackedVariablesConfig(LockingConfigurationJSON):
    """
    Represents a configuration of tracked/ignored variable names.
    """

    def __init__(self, global_scope=False, shell=None):
        if global_scope:
            path = os.path.join(get_configuration_folder(),
                                'tracked_variables.json')
        else:
            if not shell:
                raise ValueError("'shell' must be given if local scope is "
                                 "used.")
            path = os.path.join(shell.configuration_folder, 'tracking.json')

        super().__init__(path,
                         default={'default': True,
                                  'track': [],
                                  'ignore': []})

        # Load up the backing file by simulating an enter to the context.
        self.__enter__()

    def __del__(self):
        # Simulate exiting the context.
        self.__exit__()
        super().__del__()

    def track(self, variable):
        """
        Mark :param:`variable` to be tracked.
        """
        if variable in self._state['ignore']:
            self._state['ignore'].remove(variable)
        if variable not in self._state['track']:
            self._state['track'].append(variable)
        self._empty = False

    def ignore(self, variable):
        """
        Mark :param:`variable` to be ignored.
        """
        if variable not in self._state['ignore']:
            self._state['ignore'].append(variable)
        if variable in self._state['track']:
            self._state['track'].remove(variable)
        self._empty = False

    def make_default(self, variable):
        """
        Unmark :param:`variable` and use the default setting on it.
        """
        if variable in self._state['ignore']:
            self._state['ignore'].remove(variable)
        if variable in self._state['track']:
            print("removing from TRACK")
            self._state['track'].remove(variable)
        self._empty = False

    def is_tracked(self, variable):
        """
        :return: Whether :param:`variable` is to be tracked.
        """
        if variable in self._state['track']:
            return True
        if variable in self._state['ignore']:
            return False
        return self.default

    def is_explicitly_configured(self, variable):
        """
        :return: Whether :param:`variable`'s tracking status is explicitly
        configured. (Meaning that it is not the default value that is used.)
        """
        return variable in self._state['track'] or \
            variable in self._state['ignore']

    @property
    def default(self):
        """
        :return: The default tracking behaviour for variables.
        """
        return self._state['default']

    @default.setter
    def default(self, default):
        """
        Set the default tracking behaviour to :param:`default`.
        """
        self._state['default'] = bool(default)
        self._empty = False


class TrackingOverlay():
    """
    Represents an overlay of tracking configuration, which contains the global
    scope shadowed by the configuration of the local (shell) scope.
    """

    def __init__(self, shell):
        self._local = TrackedVariablesConfig(shell=shell)
        self._global = TrackedVariablesConfig(global_scope=True)

    def flush(self, global_scope=False):
        """
        Save the changes to the tracking configuration.
        """
        if global_scope:
            self._global.flush()
        else:
            self._local.flush()

    def track(self, variable, global_scope=False):
        """
        Mark :param:`variable` to be tracked.
        """
        if global_scope:
            self._global.track(variable)
        else:
            self._local.track(variable)

    def ignore(self, variable, global_scope=False):
        """
        Mark :param:`variable` to be ignored.
        """
        if global_scope:
            self._global.ignore(variable)
        else:
            self._local.ignore(variable)

    def make_default(self, variable, global_scope=False):
        """
        Unmark :param:`variable` and use the default setting on it.
        """
        if global_scope:
            self._global.make_default(variable)
        else:
            self._local.make_default(variable)

    def is_tracked(self, variable):
        """
        :return: Whether :param:`variable` is to be tracked.
        """

        if self._local.is_explicitly_configured(variable):
            return self._local.is_tracked(variable)

        if self._global.is_explicitly_configured(variable):
            return self._global.is_tracked(variable)

        return self._local.default

    def set_default(self, default, global_scope=False):
        """
        Set the default tracking behaviour to :param:`default`.
        """
        if global_scope:
            self._global.default = default
        else:
            self._local.default = default
