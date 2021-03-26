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
name = 'load'
description = \
    """Load a previously saved snapshot of environment variables' values from
    the named snapshot, and apply the changes to the current shell.

    Alternatively, this command can be used as `envprobe {SNAPSHOT`."""
help = "{{SNAPSHOT} Load the values from a named snapshot."


def command(args):
    raise NotImplementedError


def register(argparser, registered_command_list):
    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('SNAPSHOT',
                        type=str,
                        help="The name of the snapshot to load.")
    parser.add_argument('VARIABLE',
                        type=str,
                        nargs='*',
                        help="Load the values of the specified variable(s), "
                             "e.g. PATH, only.")

    mgroup = parser.add_mutually_exclusive_group()

    mgroup.add_argument('-n', '--dry-run',
                        action='store_true',
                        required=False,
                        help="Show the changes that would be loaded and "
                             "applied in the current shell, but do not "
                             "actually apply them.")
    mgroup.add_argument('-p', '--patch',
                        action='store_true',
                        required=False,
                        help="Interactively prompt and choose which changes "
                             "should be loaded.")

    parser.set_defaults(func=command)
    registered_command_list.append(name)
