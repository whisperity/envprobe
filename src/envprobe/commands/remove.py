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
from envprobe.vartypes.array import Array


name = 'remove'
description = \
    """Remove element value(s) from an environment variable.
    This command may only be used for array variables, such as PATH.


    Alternatively, this command can be accessed by calling
    envprobe -VARIABLE value1 value2 ...`."""
help = "{-VARIABLE} Remove element(s) from an array variable."


def command(args):
    try:
        env_var, _ = args.environment[args.VARIABLE]
    except KeyError:
        raise ValueError("This environment variable can not or should not be "
                         "managed through Envprobe.")

    if not isinstance(env_var, Array):
        raise TypeError("'remove' can not be called on variables that are "
                        "not arrays.")

    for val in args.VALUE:
        env_var.remove_value(val)

    args.environment.set_variable(env_var)
    args.shell.set_environment_variable(env_var)


def register(argparser, shell):
    if not (shell.is_envprobe_capable and shell.manages_environment_variables):
        return

    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('VARIABLE',
                        type=str,
                        help="The variable which the value(s) will be removed "
                             "from, e.g. PATH.")
    parser.add_argument('VALUE',
                        type=str,
                        nargs='+',
                        help="The value(s) to be removed, e.g. \"/usr/bin\". "
                             "All occurrences of the specified values will "
                             "be removed, and the list may contain "
                             "duplicates.")
    parser.set_defaults(func=command)
