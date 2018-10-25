"""
Handles managing the user's saved, named states (differences).
"""
import fcntl
import json
import os

from configuration import get_configuration_folder
from configuration.locking_configuration_json import LockingConfigurationJSON


def get_save_folder():
    return os.path.join(get_configuration_folder(), 'saves')


class Save(LockingConfigurationJSON):
    """
    Represents a single named, saved state, which is a collection of
    environment variable differences.
    This class is expected to be used as a context.
    """

    # Unset is a special value that indicates that a variable is to be unset.
    UNSET = object()

    def __init__(self, name, read_only=False):
        """
        Initialize a save with the given :param:`name`.
        """
        super().__init__(os.path.join(get_save_folder(), name + '.json'),
                         read_only,
                         default={'variables': dict(),
                                  'unset': []})

    def __iter__(self):
        """
        Retrieve a generator over the variable names that contain a change
        directive in the current save.
        """
        for key in self._state['variables'].keys():
            yield key
        for key in self._state['unset']:
            yield key

    def __getitem__(self, key):
        """
        Retrieve the difference for the variable :param:`key7.
        """
        if key in self._state['unset']:
            return Save.UNSET
        return self._state['variables'].get(key, None)

    def __setitem__(self, key, difference):
        """
        Set the value of variable :param:`key` to the given
        :param:`difference`.
        """
        if self._read_only:
            raise PermissionError("Cannot change the components of a "
                                  "read-only save.")
        self._state['variables'][key] = difference
        if key in self._state['unset']:
            self._state['unset'].remove(key)
        self._empty = False

    def __delitem__(self, key):
        """
        Mark the given :param:`key` as a variable that is to be deleted
        when the save is applied.
        """
        if self._read_only:
            raise PermissionError("Cannot change the components of a "
                                  "read-only save.")
        if key in self._state['variables']:
            del self._state['variables'][key]
        if key not in self._state['unset']:
            self._state['unset'].append(key)
        self._empty = False

    def __len__(self):
        """
        :return: The number of elements that have modifications in the save.
        """
        return len(self._state['variables']) + len(self._state['unset'])
