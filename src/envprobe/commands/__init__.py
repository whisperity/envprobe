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
"""This package implements the individual user-facing subcommands of
`envprobe (main)` that are related to interfacing with the environment
variables.
"""
from . import add, get, remove, undefine
from . import set as set_command


def register_envvar_commands(argparser, registered_command_list, shell):
    """Register the command related to environment variable processing."""
    if not (shell.is_envprobe_capable and shell.manages_environment_variables):
        return

    # The order of execution determines the order of commands, so it matters!
    get.register(argparser, registered_command_list)
    set_command.register(argparser, registered_command_list)
    undefine.register(argparser, registered_command_list)
    add.register(argparser, registered_command_list)
    remove.register(argparser, registered_command_list)
