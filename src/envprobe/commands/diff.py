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
from enum import Enum

from envprobe.environment import VariableDifferenceKind


name = 'diff'
description = \
    """Shows the difference between the current environment variables, and the
    last known saved state.

    Alternatively, this command can be accessed by calling `envprobe %`."""
help = "{%%} Shows the difference between current and saved values."


class Format(Enum):
    HUMAN_READABLE = 0
    UNIFIED = 1

    @staticmethod
    def human_readable(variable_name, diff):
        kind_to_str = {VariableDifferenceKind.CHANGED: "(!) Changed:",
                       VariableDifferenceKind.REMOVED: "(-) Removed:",
                       VariableDifferenceKind.ADDED: "(+) Added:"}
        kind = kind_to_str[diff.kind]

        print("{0} {1}".format(
            kind.ljust(max(len(s) for s in kind_to_str.values()) + 4),
            variable_name))

        action_to_str = {'new': "defined value:",
                         'unset': "value was:",
                         'add': "added:",
                         'remove': "removed:",
                         'from': "changed from:",
                         'to': "changed to:"}
        longest_action_str = max(len(s) for s in action_to_str.values())
        action_to_str = {k: v.ljust(longest_action_str)
                         for k, v in action_to_str.items()}

        if diff.is_new:
            print("\t{0} {1}".format(action_to_str['new'], diff.new_value))
        elif diff.is_unset:
            print("\t{0} {1}".format(action_to_str['unset'], diff.old_value))
        elif diff.is_simple_change:
            print("\t{0} {1}".format(action_to_str['from'], diff.old_value))
            print("\t{0} {1}".format(action_to_str['to'], diff.new_value))
        else:
            for action, value in diff.diff_actions:
                if action == '=':
                    # Ignore "unchanged" values from the human-readable output.
                    continue
                if action == '+':
                    print("\t{0} {1}".format(action_to_str['add'], value))
                elif action == '-':
                    print("\t{0} {1}".format(action_to_str['remove'], value))

        print()  # Explicit newline.

    @staticmethod
    def unified(variable_name, diff):
        old_name, new_name = variable_name, variable_name
        old_start, old_count = 1, 1
        new_start, new_count = 1, 1

        if isinstance(diff.old_value, list):
            old_count = len(diff.old_value)
        if isinstance(diff.new_value, list):
            new_count = len(diff.new_value)

        if diff.is_new:
            old_name = "/dev/null"
            old_start, old_count = 0, 0
        elif diff.is_unset:
            new_name = "/dev/null"
            new_start, new_count = 0, 0

        print("--- {0}".format(old_name))
        print("+++ {0}".format(new_name))
        print("@@ -%d,%d +%d,%d @@"
              % (old_start, old_count, new_start, new_count))
        for action, value in diff.diff_actions:
            if action == '=':
                # "Keep" actions are prefixed with a space in unified diffs.
                action = ' '
            print("{0}{1}".format(action, value))

        print()  # Explicit newline.


def command(args):
    diff = args.environment.diff()
    variables = set(args.VARIABLE) & set(diff.keys()) if args.VARIABLE \
        else set(diff.keys())

    for variable in sorted(variables):
        if not args.tracking.is_tracked(variable):
            continue

        if args.output_type == Format.HUMAN_READABLE:
            Format.human_readable(variable, diff[variable])
        elif args.output_type == Format.UNIFIED:
            Format.unified(variable, diff[variable])


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
                        nargs='*',
                        help="Show the difference only for the specified "
                             "variable(s), e.g. PATH.")

    fmt = parser.add_argument_group("output format arguments"). \
        add_mutually_exclusive_group()

    fmt.add_argument('-n', '--normal',
                     dest='output_type',
                     action='store_const',
                     const=Format.HUMAN_READABLE,
                     help="Show a \"normal\", human-readable explanation of "
                          "the difference. This is the default behaviour.")
    fmt.add_argument('-u', '--unified',
                     dest='output_type',
                     action='store_const',
                     const=Format.UNIFIED,
                     help="Show the difference in the \"unified diff\" format,"
                          " as if the standard `diff -u` was called. This "
                          "format is more suitable if a machine-readable "
                          "output is needed.")

    parser.set_defaults(func=command, output_type=Format.HUMAN_READABLE)
