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
from copy import deepcopy
import os

from envprobe.compatibility import nullcontext


K_VARIABLES = 'variables'
K_UNSETS = 'unset'


def get_snapshot_directory_name():
    """Returns the expected default name of the snapshot containing directory.

    Warning
    -------
    This method only returns the **directory name** for the snapshots, not its
    location or full path.
    """
    return "snapshots"


def get_snapshot_file_name(snapshot_name):
    """Returns the expected name of the snapshot file, given it's logical name.

    Warning
    -------
    This method only returns the file path component for the snapshot, not its
    location or full path.
    """
    return os.path.normpath(snapshot_name.lstrip('/')) + ".json"


def get_snapshot_name(snapshot_file_name):
    """Returns the logical name of the snapshot, given it's filename.

    Warning
    -------
    This method only returns the name for the filename component.
    The snapshot directory and its full path should be removed from the path
    before calling.
    """
    split = snapshot_file_name.split(".json")
    return split[0] if not split[1] else None


class Snapshot:
    """Represents a persisted configuration file of the user which stores the
    state of some environment variables.
    """

    config_schema = {K_VARIABLES: dict(),
                     K_UNSETS: set()}

    UNDEFINE = None
    """``UNDEFINE`` is a special tag instance that is returned by
    :py:class:`Snapshot` if the stored action for a variable is to undefine it.

    This value should **always** be **identity-compared** with the ``is``
    keyword.

    :meta hide-value:  (Do not show the "None" initialisation in the docs!)
    """

    def __init__(self, configuration=None):
        """Initialise a snapshot manager.

        This instantiation is cheap.
        Accessing the underlying data is only done when a query or a setter
        function is called.

        Parameters
        ----------
        configuration: context-capable dict, optional
        """
        self.UNDEFINE = object()  # Create the tag instance.
        self._config = configuration if configuration is not None \
            else nullcontext(deepcopy(self.config_schema))

    def keys(self):
        """Returns the variable names that are affected by the snapshot."""
        with self._config as conf:
            return set(conf[K_UNSETS]) | set(conf[K_VARIABLES].keys())

    def __getitem__(self, variable_name):
        """Retrieve the stored actions for the given variable.

        Returns
        -------
        diff_actions : list(char, str)
            The representation of the diff actions to be taken for the variable
            to have the value in the saved snapshot.

            See :py:meth:`envprobe.vartypes.EnvVar.diff` for the format.
        :py:attr:`UNDEFINE`
            Returned if the variable was marked to be undefined.
        """
        with self._config as conf:
            if variable_name in conf[K_UNSETS]:
                return self.UNDEFINE
            return conf[K_VARIABLES].get(variable_name, None)

    def __setitem__(self, variable_name, difference):
        """Sets the stored action of the given variable to the new value.

        Parameters
        ----------
        variable_name : str
            The name of the variable to set.
        difference : list(char, str)
            The difference actions to save into the snapshot file.

            See :py:meth:`envprobe.vartypes.EnvVar.diff` for the format.

        Warning
        -------
        :py:meth:`__setitem__` **overwrites** the information that is stored
        in the snapshot.
        In most cases, :py:meth:`envprobe.vartypes.EnvVar.merge_diff` should be
        used to first create a diff that appends to the current one, and save
        that result.
        """
        with self._config as conf:
            if variable_name in conf[K_UNSETS]:
                del conf[K_UNSETS][variable_name]
            conf[K_VARIABLES][variable_name] = difference

    def __delitem__(self, variable_name):
        """Marks the given variable to be undefined when the snapshot is
        loaded.

        Parameters
        ----------
        variable_name : str
            The name of the variable to mark for undefinition.
        """
        with self._config as conf:
            if variable_name in conf[K_VARIABLES]:
                del conf[K_VARIABLES][variable_name]
            conf[K_UNSETS].add(variable_name)
