"""
Handles managing the user's saved, named states (differences).
"""
import fcntl
import json
import os

from configuration import get_configuration_folder


def get_save_folder():
    return os.path.join(get_configuration_folder(), 'saves')


class Save():
    """
    Represents a single named, saved state, which is a collection of
    environment variable differences.
    This class is expected to be used as a context.
    """

    # Unset is a special value that indicates that a variable is to be unset.
    UNSET = object()

    def __init__(self, name, read_only=False):
        """
        Initialize a save with the given :param:`name`. The constructor makes
        sure the save's backend file works and is accessible.
        """
        self._empty = True
        self._read_only = read_only
        self._state = {'variables': dict(),
                       'unset': []}

        save_folder = get_save_folder()
        if not os.path.isdir(save_folder):
            os.makedirs(save_folder, 0o0700)

        self._save_file = os.path.join(save_folder, name + '.json')
        if not os.path.isfile(self._save_file):
            # Create an empty file if the save does not exist yet.
            with open(self._save_file, 'w') as f:
                pass
            os.chmod(self._save_file, 0o0600)

    def __del__(self):
        # In case the save's file was only initialised and locked because
        # the user attempted to create the save but never actually modified
        # anything, an empty file would be left behind. Remove it.
        if self._empty:
            os.unlink(self._save_file)

    def _close(self):
        if self._handle:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
            self._handle.close()

            self._handle = None

    def delete_file(self):
        """
        Delete the current save's file from the disk.
        """
        if self._read_only:
            raise PermissionError("Cannot delete a read-only save.")

        self._close()
        self._read_only = True
        self._state = None
        self._empty = None

        os.unlink(self._save_file)

    def __enter__(self):
        """
        Enter access mode with the save file. This method will open, lock and
        keep the file handle.
        """
        self._handle = open(self._save_file,
                            'r' if self._read_only else 'r+')

        lock_mode = fcntl.LOCK_SH if self._read_only else fcntl.LOCK_EX
        lock_mode = lock_mode ^ fcntl.LOCK_NB
        try:
            fcntl.flock(self._handle.fileno(), lock_mode)
        except BlockingIOError:
            return None

        self._load_state()
        return self

    def __exit__(self, *exc):
        """
        Unlock the save file and close the connection. Note that this method
        does NOT write the changes (if any) to the disk, for that use
        :func:`flush()`.
        """
        self._close()

    def _load_state(self):
        self._handle.seek(0)
        d = dict()
        try:
            d = json.load(self._handle)
            self._empty = False
        except json.JSONDecodeError:
            # If the JSON file is bogus (e.g. it was created just in
            # `__init__`), ignore it and run with the default state.
            pass
        self._state.update(d)

    def flush(self):
        """
        Actually write the current :type:`Save` onto the disk.
        """
        if self._read_only:
            raise PermissionError("Cannot change the components of a "
                                  "read-only save.")
        try:
            self._handle.seek(0)
            self._handle.truncate(0)

            json.dump(self._state, self._handle,
                      indent=2, sort_keys=True)
        except TypeError:
            raise

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
