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
"""Implements the lazy dynamic loading mechanism for user-facing commands."""
import importlib
import os


__MODULES_TO_COMMANDS = {}
__COMMANDS_TO_MODULES = {}


def get_module(name):
    """Retrieves the implementation module for the command of the given name.

    Parameters
    ----------
    name : str
        The name of the command to load.

    Returns
    -------
    module
        The implementation module.

    Raises
    ------
    KeyError
        Raised if the given `name` is not registered.
    """
    return __COMMANDS_TO_MODULES[name]


def get_command(module):
    """Retrieves the command name for the specified implementation module.

    Parameters
    ----------
    module : module
        The implementation `module`.

    Returns
    -------
    str
        The user-facing name of the command.

    Raises
    ------
    KeyError
        Raised if the given `module` is not registered.
    """
    return __MODULES_TO_COMMANDS[module]


def get_known_commands():
    """Get the list of dynamically registered and loaded commands.

    Returns
    -------
    list(str)
        The command names.
    """
    return __COMMANDS_TO_MODULES.keys()


def load(command):
    """Attempt to load a command implementation.

    Parameters
    ----------
    command : str
        The name of the command module to load.

    Returns
    -------
    module
        If the loading succeeded or the given `command` is already registered,
        the module implementation is returned.

    Raises
    ------
    ModuleNotFoundError
        Raised if the module to load is not found.
    """
    try:
        return get_command(command)
    except KeyError:
        pass

    try:
        mod = importlib.import_module("envprobe.commands.{0}".format(command))
    except ModuleNotFoundError:
        raise

    __MODULES_TO_COMMANDS[mod] = command
    __COMMANDS_TO_MODULES[command] = mod
    return mod


def load_all():
    """Loads all command implementations to the interpreter found under
    :py:mod:`envprobe.commands` in the install.
    """
    for f in os.listdir(os.path.dirname(__loader__.path)):
        module_name = f.split('.')[0]
        if not (module_name and f.endswith('.py')):
            continue
        load(module_name)
