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


name = 'add'
description = \
    """Add element value(s) to an environment variable.
    This command may only be used for array variables, such as PATH.

    Alternatively, this command can be accessed by calling
    `envprobe +VARIABLE value1 value2 ...` for appending to the front,
    or `envprobe VARIABLE+ value1 value2 ...` for appending to the back."""
help = "{+VARIABLE} Add element(s) to an array variable."
position_help = \
    """(default: 0) The position/index in the array where the inserted
    elements should start at after insertion.
    The elements to the right (later, higher index) in the array will be
    shifted further to the right.

    A positive value will mean a position from the beginning, with 0
    representing the first element.
    A negative value means a position from the back of the array, with -1
    pointing to the last element.

    Adding at position 0 is equivalent to appending to the front of the
    array, while adding at -1 means appending at the back of the array."""
epilogue = \
    """For example, calling `envprobe add --position 1 VAR foo bar` for a
    variable that currently looks like this: [0, 1, 2] will result in "foo"
    being placed at index 1, and thus turning the variable to:
    [0, foo, bar, 1, 2].

    Similarly, in the case of a negative index, the indexing of the array
    positions follow the scheme: [-3, -2, -1] and specifying `--position -2`
    in the above example will produce the same end result:
    [-3, foo, bar, -2, -1]."""


def command(args):
    try:
        env_var, _ = args.environment[args.VARIABLE]
    except KeyError:
        raise ValueError("This environment variable can not or should not be "
                         "managed through Envprobe.")

    if not isinstance(env_var, Array):
        raise TypeError("'add' can not be called on variables that are "
                        "not arrays.")

    for val in args.VALUE:
        env_var.insert_at(args.position, val)
        if args.position >= 0:
            # The arguments in VALUE are appended sequentially, so in case
            # of a positive index, the insert location should be kept in sync.
            # For negative insert indices, the shifting takes care of this
            # automatically.
            args.position += 1

    args.environment.set_variable(env_var)
    args.shell.set_environment_variable(env_var)


def register(argparser, shell):
    if not (shell.is_envprobe_capable and shell.manages_environment_variables):
        return

    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help,
            epilog=epilogue
    )

    parser.add_argument('VARIABLE',
                        type=str,
                        help="The variable which the value(s) will be added "
                             "to, e.g. PATH.")
    parser.add_argument('VALUE',
                        type=str,
                        nargs='+',
                        help="The value(s) to be added, e.g. \"/usr/bin\". "
                             "The list may contain duplicates.")
    parser.add_argument('--position',
                        type=int,
                        required=False,
                        default=0,
                        help=position_help)

    parser.set_defaults(func=command)
