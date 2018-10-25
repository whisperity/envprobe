import fcntl
import json
import os


class LockingConfigurationJSON():
    """
    A helper class that maps a dictionary-based configuration object to a
    JSON configuration file on the disk.
    This class is expected to be used as a context.
    """

    def __init__(self, path, read_only=False,
                 dir_mode=0o0700, file_mode=0o0600,
                 default=None):
        """
        Initialise a new configuration file at the given :param:`path`.

        :param read_only: If True, the file will be opened only for reading
        and won't be locked exclusively when entered into the context.
        """
        self._empty = True
        self._read_only = read_only
        self._state = dict() if default is None else default

        folder = os.path.dirname(path)
        if not os.path.isdir(folder):
            os.makedirs(folder, dir_mode)

        self._path = path
        if not os.path.isfile(self._path):
            # Create an empty file if the configuration file doesn't exist.
            with open(self._path, 'w') as f:
                pass
            os.chmod(self._path, file_mode)

    def __del__(self):
        # In case the file was only initialised and locked because
        # the user attempted to access it but never actually modified
        # anything, an empty file would be left behind. Remove it.
        if self._empty:
            os.unlink(self._path)

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
            raise PermissionError("Cannot delete a read-only file.")

        self._close()
        self._read_only = True
        self._state = None
        self._empty = None

        os.unlink(self._path)

    def __enter__(self):
        """
        Enter access mode with the save file. This method will open, lock and
        keep the file handle.
        """
        self._handle = open(self._path,
                            'r' if self._read_only else 'r+')

        lock_mode = fcntl.LOCK_SH if self._read_only else fcntl.LOCK_EX
        lock_mode = lock_mode ^ fcntl.LOCK_NB
        try:
            fcntl.flock(self._handle.fileno(), lock_mode)
        except BlockingIOError:
            return None

        self.load()
        return self

    def __exit__(self, *exc):
        """
        Unlock the file and close the connection. Note that this method
        does NOT write the changes (if any) to the disk, for that use
        :func:`flush()`.
        """
        self._close()

    def load(self):
        self._handle.seek(0)
        try:
            d = json.load(self._handle)
            self._state.update(d)
            self._empty = False
        except json.JSONDecodeError:
            # If the JSON file is bogus (e.g. it was created just in
            # `__init__`), ignore it and run with the default state.
            pass

    def flush(self):
        """
        Actually write the current file to the disk.
        """
        if self._read_only:
            raise PermissionError("Cannot change the components of a "
                                  "read-only file.")
        try:
            self._handle.seek(0)
            self._handle.truncate(0)

            json.dump(self._state, self._handle,
                      indent=2, sort_keys=True)
        except TypeError:
            raise

    def __iter__(self):
        return iter(self._state)

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        if self._read_only:
            raise PermissionError("Cannot change the components of a "
                                  "read-only file.")
        self._state[key] = value
        self._empty = False

    def __delitem__(self, key):
        if self._read_only:
            raise PermissionError("Cannot change the components of a "
                                  "read-only file.")
        del self._state[key]
        self._empty = False

    def __len__(self):
        return len(self._state)
