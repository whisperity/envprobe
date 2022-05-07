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
import os

from envprobe.environment import Environment, default_heuristic
from envprobe.settings import core as settings
from envprobe.settings import config_file, snapshot, variable_information, \
    variable_tracking
from envprobe.shell import get_current_shell, FakeShell


def get_shell_and_env_always(env_dict=None, vartype_pipeline=None):
    """Return an :py:class:`environment.Environment` and
    :py:class:`shell.Shell`, no matter what.

    Parameters
    ----------
    env_dict : dict, optional
        The raw mapping of environment variables to their values, as in
        :py:data:`os.environ`.
    vartype_pipeline : envprobe.environment.HeuristicStack, optional
        The type resolution heuristics pipeline to use.
        If not specified, the :py:data:`.environment.default_heuristic` will
        be used.

    Returns
    -------
    shell : .shell.Shell
        The shell which use can be deduced from the current environment (by
        calling :py:func:`.shell.get_current_shell`).
        If none such can be deduced, a :py:class:`.shell.FakeShell` is
        returned, which is a **valid** :py:class:`.shell.Shell` subclass that
        tells the client code it is not capable of anything.
    env : .environment.Environment
        The environment associated with the current context and the
        instantiated `Shell`.
    """
    if not env_dict:
        env_dict = os.environ
    if not vartype_pipeline:
        vartype_pipeline = default_heuristic

    try:
        sh = get_current_shell(env_dict)
    except KeyError:
        sh = FakeShell()

    env = Environment(sh, env_dict, vartype_pipeline)

    return sh, env


def get_snapshot(snapshot_name, read_only=True):
    """Creates the snapshot instance for the snapshot of the given name.

    Parameters
    ----------
    snapshot_name : str
        The name of the snapshot to load or create.
    read_only : bool
        If ``True``, the file will be opened read-only and not saved at exit.

    Returns
    -------
    .settings.snapshot.Snapshot
        The snapshot manager object.
        Access to the underlying file is handled automatically through this
        instance.
    """
    basedir = os.path.join(settings.get_configuration_directory(),
                           snapshot.get_snapshot_directory_name())
    return snapshot.Snapshot(
        config_file.ConfigurationFile(
            os.path.join(basedir,
                         snapshot.get_snapshot_file_name(snapshot_name)),
            snapshot.Snapshot.config_schema,
            read_only=read_only)
    )


def get_variable_information_manager(variable_name, read_only=True):
    """Creates the extended information attribute manager for environment
    variables based on the requested variable's name.

    Parameters
    ----------
    varable_name : str
        The name of the variable to configure.
    read_only : bool
        If ``True``, the associated file will be opened read-only and not saved
        at exit.

    Returns
    -------
    .settings.variable_information.VariableInformation
        The configuration handler engine.
        Access to the underlying file is handled automatically through this
        instance.
    """
    basedir = os.path.join(settings.get_configuration_directory(),
                           variable_information.get_variable_directory_name())

    return variable_information.VariableInformation(
        config_file.ConfigurationFile(
            os.path.join(basedir,
                         variable_information.get_information_file_name(
                             variable_name)),
            variable_information.VariableInformation.config_schema,
            read_only=read_only)
    )


def get_variable_tracking(shell=None):
    """Creates a **read-only** tracking manager for the standard global and
    local configuration files.

    Parameters
    ----------
    shell : .shell.Shell, optional
        The shell which is used in the current environment, used to retrieve
        the local configuration directory.

    Returns
    -------
    .settings.variable_tracking.VariableTracking
        The tracking handler engine.
        The configuration files are opened **read-only**.
    """
    if shell and shell.is_envprobe_capable:
        local_config_file = config_file.ConfigurationFile(
            os.path.join(shell.configuration_directory,
                         variable_tracking.get_tracking_file_name()),
            variable_tracking.VariableTracking.config_schema_local,
            read_only=True)
    else:
        local_config_file = None

    global_config_file = config_file.ConfigurationFile(
        os.path.join(settings.get_configuration_directory(),
                     variable_tracking.get_tracking_file_name()),
        variable_tracking.VariableTracking.config_schema_local,
        read_only=True)

    return variable_tracking.VariableTracking(global_config_file,
                                              local_config_file)
