# Copyright (C) 2018 Whisperity
#
# SPDX-License-Identifier: GPL-3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from contextlib import AbstractContextManager
from copy import deepcopy
import fcntl
from io import UnsupportedOperation
import json
import os
import random
import stat
import string


class LockedFileHandle(AbstractContextManager):
    """A file handle wrapper over :py:func:`open` that locks the underlying
    file before operation.
    """

    def __init__(self, path, mode='r', blocking=True, force_exclusive=False):
        """Creates a new locked handle and opens the file.

        Parameters
        ----------
        path : str
            The file to open.
        mode : str, optional
            The mode argument, as passed to :py:func:`open`.
            Conventionally, this is either ``'r'`` for reading, or
            ``'w'``/``'a'`` for writing/appending.

            If the file is open for writing, an exclusive lock will be created,
            if only for reading, a shared lock will be created.
        blocking : bool, optional
            If `False`, the lock will be acquired in "non-blocking mode", which
            will result in a :py:class:`OSError` being raised if the file is
            already locked in an incompatible mode, i.e. open for reading when
            another process wants to write.
        force_exclusive : bool, optional
            If `True`, the file will be opened and locked exclusively, no
            matter what.
        """
        self._cookie = ''.join([random.choice(string.ascii_lowercase)  # nosec
                                for _ in range(8)]) + '/' + str(os.getpid())
        self._handle = None
        self._lockfd = None
        self._lock_path = path + ".lock"
        self._mode = mode
        self._path = path

        self._lock_type = fcntl.LOCK_SH
        self._lock_text = "sh"
        if 'w' in mode or 'a' in mode or 'x' in mode or '+' in mode:
            self._lock_type = fcntl.LOCK_EX
            self._lock_text = "ex"

        if force_exclusive:
            self._lock_type = fcntl.LOCK_EX
            self._lock_text = "ex!"

        if not blocking:
            self._lock_type = self._lock_type | fcntl.LOCK_NB
            self._lock_text = "?" + self._lock_text

    def _update_lockline(self, unlock):
        """Updates the line associated with the current lock in the file."""
        # We will use an fcntl lock on the *main* file **always** in exclusive
        # mode to "lock" the lockfile when its contents are being updated.
        if not self._lockfd or not self._handle:
            raise EnvironmentError("Tried to lockline without open handles!")

        try:
            fcntl.flock(self._handle, fcntl.LOCK_EX)

            self._lockfd.seek(0)
            locklines = self._lockfd.readlines()
            locklines = list(filter(
                lambda l: l != '\n' and
                not l.startswith(self._cookie), locklines))
            if not unlock:
                locklines.append("{0}:{1}".format(self._cookie,
                                                  self._lock_text))

            self._lockfd.seek(0)
            self._lockfd.truncate(0)
            self._lockfd.write(''.join(locklines) + '\n')
            self._lockfd.flush()
        finally:
            fcntl.flock(self._handle, fcntl.LOCK_UN)

    def acquire(self):
        """Acquires the lock.

        Returns
        -------
        file object
            The opened file handle, as if :py:func:`open` was called.

        Raises
        ------
        OSError
            :py:class:`OSError` is raised the same way and reasons
            :py:func:`open` would raise them, in addition to the
            *"Resource temporarily unavailable"* (:py:data:`errno.EAGAIN`)
            if a *non-blocking* lock was requested and the lock cannot be
            acquired.
        """
        if self._lockfd:
            return self._handle

        try:
            self._lockfd = open(self._lock_path, 'r+')
        except OSError:
            # The file did not exist for reading, so create it now.
            self._lockfd = open(self._lock_path, 'w+')
            self._lockfd.flush()

        try:
            fcntl.flock(self._lockfd, self._lock_type)
        except OSError:
            self.release()
            raise

        try:
            self._handle = open(self._path, self._mode)
            self._update_lockline(unlock=False)
            return self._handle
        except Exception:
            self.release()
            raise

    def release(self):
        """Releases the lock and closes the file."""
        if not self._lockfd:
            return

        if self._handle:
            self._update_lockline(unlock=True)
            self._handle.close()
            self._handle = None

        fcntl.flock(self._lockfd, fcntl.LOCK_UN)

        self._lockfd.close()
        self._lockfd = None

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()


def json_extended_encoder(obj):
    """Allows encoding additional Python types normally not supported or using
    a different representation.
    """
    if isinstance(obj, list):
        return [json_extended_encoder(e) for e in obj]
    if isinstance(obj, dict):
        return {k: json_extended_encoder(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return {"__TYPE__": 'S',
                '_': list(map(json_extended_encoder, obj))
                }
    if isinstance(obj, tuple):
        # Sadly, json.JSONEncoder subclassing default() has a "bug", and
        # doesn't call default() in a subclass for types it can already encode.
        # (See http://bugs.python.org/issue30343.)
        return {"__TYPE__": 'T',
                '_': list(map(json_extended_encoder, obj))
                }

    return obj


def json_extended_decoder(obj):
    """Allows decoding additional Python types normally not supported or using
    a different representation.
    """
    if isinstance(obj, list):
        return [json_extended_decoder(e) for e in obj]
    if isinstance(obj, dict):
        type_id = obj.get("__TYPE__", None)
        if type_id == 'S':
            return set(obj['_'])
        if type_id == 'T':
            return tuple(obj['_'])

        return {k: json_extended_decoder(v) for k, v in obj.items()}

    return obj


class ConfigurationFile(AbstractContextManager):
    """A glorified :py:class:`dict` that is backed into a JSON file and locked
    on access.

    This class embeds file locking logic to ensure atomic access to the backing
    file is given.
    """

    def __init__(self, file_path, default_content=None, read_only=False,
                 file_mode=stat.S_IRUSR | stat.S_IWUSR,
                 directory_mode=stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR):
        """Initialise a configuration file.

        Parameters
        ----------
        file_path : str
            The path of the backing file of the configuration storage.
        default_content : dict, optional
            The contents of the configuration if the backing file does not
            exist.
        read_only : bool, optional
            Whether the configuration is opened read-only.
            Creating the configuration read-only will prevent any changes from
            being applied from Python code, and will also prevent the backing
            file from writing.
        file_mode : int, optional
            If the backing file does not exist, it will be created with the
            mode flags given.
            Defaults to *owner read, write*, no execute permission, or
            permissions for group and world.
        directory_mode : int, optional
            If the directory where the backing file should be put does not
            exist, it will be created with the mode flags given.
            Defaults to *owner read, write, list*, no permission for group
            and world.
        """
        self._data = deepcopy(default_content if default_content else dict())
        self._dmode = directory_mode
        self._fmode = file_mode
        self._in_context = False
        self._last_loaded_data = deepcopy(self._data)
        self._read_only = read_only
        self._path = file_path

    def load(self):
        """Load the contents of the backing file into memory.

        Warning
        -------
        After the file's contents are loaded into memory, the lock is
        **released**, meaning that subsequent changes in the file might be
        overwritten if :py:func:`save` is called with the current contents!

        If you intend to *change* the configuration and save it, use
        `ConfigurationFile` as a context manager instead.
        """
        if self._in_context:
            raise EnvironmentError("Do not call load() if a context (with) is "
                                   "already acquired!")

        try:
            with LockedFileHandle(self._path, 'r') as f:
                try:
                    self._load_data(f)
                except Exception:
                    self._data = deepcopy(self._last_loaded_data)
                    raise
        except OSError:
            # Ignore, the class has been constructed with default data anyways.
            pass

    def _load_data(self, fd):
        """Actually load the data from the `fd` file."""
        fd.seek(0)
        data = json.load(fd)
        data = json_extended_decoder(data)
        self._data.update(data)  # Merge the changes with the defaults.

        self._last_loaded_data = deepcopy(self._data)

    def save(self):
        """Save the contents of memory to the backing file.

        Raises
        ------
        io.UnsupportedOperation
            Raised if the file was opened `read_only`, but `save` is called.

        Warning
        -------
        The file's contents are **overwritten** by this method after acquiring
        the lock, destroying potential changes that might have been written
        before.
        The lock is released afterwards immediately.

        If you intend to *change* the configuration in one go, use
        `ConfigurationFile` as a context manager instead.
        """
        if self._in_context:
            raise EnvironmentError("Do not call save() if a context (with) is "
                                   "already acquired!")

        if self._read_only:
            raise UnsupportedOperation("Not writable.")

        if not self._data and not self.changed:
            return

        self._try_create_file()
        try:
            with LockedFileHandle(self._path, 'w') as f:
                try:
                    self._save_data(f)
                except Exception:
                    raise
        except OSError:
            raise

    def _try_create_file(self):
        """Tries to create the location where the backing file is.

        Returns
        -------
        file_exists : bool
            Whether the file originally existed, in which case this method did
            nothing.
        """
        file_exists = os.path.isfile(self._path)
        if not file_exists:
            dir_path = os.path.dirname(self._path)
            if dir_path and not os.path.isdir(dir_path):
                os.makedirs(dir_path, self._dmode)
            with open(self._path, 'w') as f:
                json.dump(dict(), f)
            os.chmod(self._path, self._fmode)
        return file_exists

    def _save_data(self, fd):
        """Actually save the data to the `fd` file."""
        fd.seek(0)
        fd.truncate(0)

        try:
            data_to_dump = json_extended_encoder(self._data)
            json.dump(data_to_dump, fd, indent=2, sort_keys=True)
            self._last_loaded_data = deepcopy(self._data)
        except Exception:
            # Restore the last good state in the file.
            fd.seek(0)
            fd.truncate(0)
            json.dump(self._last_loaded_data, fd, indent=2, sort_keys=True)
            raise

    def __enter__(self):
        """Acquires the backing file, read its contents, and return a context
        where the `ConfigurationFile` can be used.

        Returns
        -------
        ConfigurationFile
            The `self` instance.

        Note
        ----
        This method should be used instead of :py:func:`load` and
        :py:func:`save` if a changing access to the contents is expected,
        as the context keeps the lock on the file active throughout.
        """
        self._try_create_file()

        # TODO: Allow multiple enter calls, and make sure the lock is only
        # open once.

        self._in_context = LockedFileHandle(self._path,
                                            'r' if self._read_only else 'r+')
        handle = self._in_context.acquire()
        try:
            self._load_data(handle)
        except Exception:
            self._in_context.release()
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Saves the changes to the current file (if not read-only) and
        releases the lock.
        """
        if not self._read_only and self._data and self.changed:
            handle = self._in_context.acquire()
            try:
                self._save_data(handle)
            except Exception:
                self._in_context.release()
                self._in_context = False
                raise
        elif self._read_only and not self._data and not self.changed:
            # The saving would've happened to an empty file which got created
            # by __enter__(), so delete it instead.
            os.remove(self._path)

        self._in_context.release()
        self._in_context = False

    @property
    def changed(self):
        """Returns whether the data in memory changed since the last save
        or load.
        """
        return self._data != self._last_loaded_data

    def __len__(self):
        """Returns the number of keys in memory."""
        return len(self._data)

    def __iter__(self):
        """Returns an iterator over the data loaded to memory."""
        return iter(self._data)

    def __contains__(self, key):
        """Returns if the data in memory contains `key`."""
        return key in self._data

    def get(self, key, default=None):
        """Returns the data in memory for `key`, or if no `key` found,
        `default`.
        """
        return self._data.get(key, default)

    def __getitem__(self, key):
        """Retrieves the element for `key`."""
        return self._data[key]

    def __setitem__(self, key, value):
        """Sets the element for `key` to `value`."""
        if self._read_only:
            raise PermissionError("Read-only configuration file.")
        self._data[key] = value

    def __delitem__(self, key):
        """Deletes the `key`."""
        if self._read_only:
            raise PermissionError("Read-only configuration file.")
        del self._data[key]
