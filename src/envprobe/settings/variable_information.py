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

from envprobe.compatibility import nullcontext


K_VARIABLES = 'variables'
K_VARIABLE_TYPE = 'type'
K_VARIABLE_CONFIGURATION_SOURCE = 'source'
K_VARIABLE_DESCRIPTION = 'description'


def get_variable_directory_name():
    """Returns the expected default name of the variable detail directory.

    Warning
    -------
    This method only returns the **directory name** for the variables, not its
    location or full path.
    """
    return "variables"


def get_information_file_name(variable_name):
    """Returns the expected name of the file containing information for the
    given variable.

    Warning
    -------
    This method only returns the file name component for the backing file, not
    its location or full path.
    """
    # Translate the variable name into a grouping based on the first character
    # of the name. This is to ensure that the files don't grow *too* big.
    return variable_name[0] + ".json"


class VariableInformation:
    """Represents a persisted configuration file of the user which stores
    additional information about environment variables.
    """

    config_schema = {K_VARIABLES: dict()}

    def __init__(self, configuration=None):
        """Initialise a variable configuration manager.

        This instantiation is cheap.
        Accessing the underlying data is only done when a query or a setter
        function is called.

        Parameters
        ----------
        configuration: context-capable dict, optional
        """
        self._config = configuration if configuration is not None \
            else nullcontext(deepcopy(self.config_schema))

    def keys(self):
        """Returns the variable names that have a configuration."""
        with self._config as conf:
            return conf[K_VARIABLES].keys()

    def __getitem__(self, variable_name):
        """Retrieve the configuration for the given variable.

        Returns
        -------
        config : dict
            The configuration mapping associated with the variable.
            This can be used to instantiate an
            :py:class:`envprobe.vartypes.envvar.EnvVarExtendedInformation`.
        """
        with self._config as conf:
            if variable_name in conf[K_VARIABLES]:
                return conf[K_VARIABLES][variable_name]
            return None

    def set(self, variable_name, configuration, source):
        """Sets the stored configuration of the given variable to a new value.

        Parameters
        ----------
        variable_name : str
            The name of the variable to set.
        config : envprobe.vartypes.envvar.EnvVarExtendedInformation
            The configuration associated with the variable.
            This is automatically mapped to the persisted representation.
        source : str
            The identifier of the configuration source repository to annotate
            the saved configuration with.
        """
        with self._config as conf:
            conf[K_VARIABLES][variable_name] = \
                {K_VARIABLE_DESCRIPTION: configuration.description,
                 K_VARIABLE_TYPE: configuration.type,
                 K_VARIABLE_CONFIGURATION_SOURCE: source
                 }

    def __delitem__(self, variable_name):
        """Removes the configuration associated with the given variable.

        Parameters
        ----------
        variable_name : str
            The name of the variable to remove.
        """
        with self._config as conf:
            if variable_name in conf[K_VARIABLES]:
                del conf[K_VARIABLES][variable_name]
