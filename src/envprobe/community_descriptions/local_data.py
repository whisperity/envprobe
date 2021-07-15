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
"""
Provides access to the local data files installed from the community
descriptions project.
"""
from copy import deepcopy
import os

from envprobe.compatibility import nullcontext
from envprobe.settings import config_file, get_data_directory, \
    variable_information


def _local_data_root():
    return os.path.join(get_data_directory(), "descriptions")


def get_description_config_file_name():
    """Returns the expected default name of the master configuration file of
    the local storage.

    Warning
    -------
    This method only returns the **file name**, not its location or full path.
    """
    return "meta.json"


K_FORMAT = "format"
K_COMMIT = "commit_sha"
K_SOURCES = "sources"
K_SOURCE_COMMENT = "comment"


class MetaConfiguration:
    """Represents a persisted configuration file of the local description
    storage.
    """

    config_schema = {K_COMMIT: '0' * 41,
                     K_SOURCES: dict()
                     }

    _sources_schema = {K_SOURCE_COMMENT: None
                       }

    def __init__(self, configuration=None):
        """Initialises the metadata configuration manager.

        This instantiation is cheap.
        Accessing the underlying data is only done when a query or a setter
        function is called.

        Parameters
        ----------
        configuration: context-capable dict, optional
        """
        self._config = configuration if configuration is not None \
            else nullcontext(deepcopy(self.config_schema))

    @property
    def version(self):
        """Returns the commit identifier of the data in the storage."""
        with self._config as conf:
            return conf[K_COMMIT]

    @version.setter
    def version(self, value):
        """Sets the commit identifier of the data to the given value."""
        with self._config as conf:
            conf[K_COMMIT] = value

    def _ensure_source(self, conf, source):
        """Ensure that the record for a source entry is present."""
        if source not in conf[K_SOURCES]:
            conf[K_SOURCES][source] = deepcopy(self._sources_schema)

    def delete_source(self, source):
        """Delete the record associated with the given source."""
        with self._config as conf:
            if source in conf[K_SOURCES]:
                del conf[K_SOURCES][source]

    def get_comment_for(self, source):
        """Returns the textual comment associated with the given
        information source.
        """
        with self._config as conf:
            return conf[K_SOURCES][source][K_SOURCE_COMMENT]

    def set_comment_for(self, source, comment):
        """Save the textual comment associated with the given information
        source.
        """
        with self._config as conf:
            self._ensure_source(conf, source)
            conf[K_SOURCES][source][K_SOURCE_COMMENT] = comment


def get_storage_configuration(read_only=True):
    """Returns the configuration manager for the metainformation about the
    local storage.
    """
    return MetaConfiguration(
        config_file.ConfigurationFile(
            os.path.join(_local_data_root(),
                         get_description_config_file_name()),
            MetaConfiguration.config_schema,
            read_only=read_only)
    )


def generate_variable_information_managers():
    """Generates the manager objects for all datafiles that are present in the
    data directory for variable information storage.

    These managers are **read-only**.
    """
    basedir = os.path.join(_local_data_root(),
                           variable_information.get_variable_directory_name())

    try:
        if not os.path.isdir(basedir):
            return None
    except OSError:
        return None

    for file in os.listdir(basedir):
        if not file.endswith(".json"):
            continue

        yield variable_information.VariableInformation(
            config_file.ConfigurationFile(
                os.path.join(basedir, file),
                variable_information.VariableInformation.config_schema,
                read_only=True)
        )


def get_variable_information_manager(variable_name, read_only=True):
    """Creates the extended information attribute manager for environment
    variables based on the requested variable's name, using the locally
    installed community descriptions data as source.

    Parameters
    ----------
    varable_name : str
        The name of the variable to configure.
    read_only : bool
        If ``True``, the associated file will be opened read-only and not saved
        at exit.

    Returns
    -------
    envprobe.settings.variable_information.VariableInformation
        The configuration handler engine.
        Access to the underlying file is handled automatically through this
        instance.
    """
    basedir = os.path.join(_local_data_root(),
                           variable_information.get_variable_directory_name())

    return variable_information.VariableInformation(
        config_file.ConfigurationFile(
            os.path.join(basedir,
                         variable_information.get_information_file_name(
                             variable_name)),
            variable_information.VariableInformation.config_schema,
            read_only=read_only)
    )
