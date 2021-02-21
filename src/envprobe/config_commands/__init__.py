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
"""This package implements the individual user-facing subcommands for
`envprobe config` that are related to setting the configuration of Envprobe
both on the user and the shell level.
"""
from . import hook, track


def register_shell_commands(argparser, shell):
    """Registers the commands related to shell management."""
    if shell.is_envprobe_capable:
        return

    hook.register(argparser)


def register_tracking_commands(argparser, shell):
    """Registers the commands related to configuring variable tracking."""
    manage_local_config = shell.is_envprobe_capable and \
        shell.manages_environment_variables

    track.register(argparser, manage_local_config)
