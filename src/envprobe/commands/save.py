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
from envprobe.library import get_snapshot


name = 'save'
description = \
    """Create or update a named snapshot which will contain the values of
    environment variables.

    Alternatively, this command can be used as `envprobe }SNAPSHOT`."""
help = "{}SNAPSHOT} Save changes in the environment to a named snapshot."


def prompt():
    user_input = input("Save this change? (y/N) ").lower()
    return user_input in ['y', 'yes']


def command(args):
    diff = args.environment.diff()
    variables = set(args.VARIABLE) & set(diff.keys()) if args.VARIABLE \
        else set(diff.keys())
    if not variables:
        return

    def actually_do_something():
        return not args.patch or prompt()

    snapshot = get_snapshot(args.SNAPSHOT, read_only=False)
    for variable in sorted(variables):
        if not args.tracking.is_tracked(variable):
            continue

        var, _ = args.environment[variable]
        vdiff = diff[variable]
        if vdiff.is_new:
            # If a variable is new, save the current (existing) value.
            print("New variable '{0}' with value '{1}'."
                  .format(variable, vdiff.new_value))
            if actually_do_something():
                snapshot[variable] = vdiff.new_value

                # apply_change() marks a change to be saved in the pristine
                # environment, rendering it no longer changed.
                args.environment.apply_change(var)
        elif vdiff.is_unset:
            # If a variable is unset, save this fact.
            print("Variable '{0}' (from value '{1}') undefined."
                  .format(variable, vdiff.old_value))
            if actually_do_something():
                del snapshot[variable]
                args.environment.apply_change(var, remove=True)
        elif vdiff.is_simple_change:
            # If the change is a simple change, we are still only
            # interested in persisting the new value.
            print("Variable '{0}' changed from '{1}' to '{2}'."
                  .format(variable, vdiff.old_value, vdiff.new_value))
            if actually_do_something():
                snapshot[variable] = vdiff.new_value
                args.environment.apply_change(var)
        else:
            # For more complex changes, we have to handle the changes
            # one-by-one.
            diff_in_snapshot = snapshot[variable]
            if not diff_in_snapshot:
                diff_in_snapshot = list()

            current_diff = list()
            for mode, value in vdiff.diff_actions:
                if mode == '=':
                    # Ignore unchanged values.
                    continue
                elif mode == '-':
                    print("For variable '{0}' the element '{1}' was "
                          "removed.".format(variable, value))
                elif mode == '+':
                    print("For variable '{0}' the element '{1}' was "
                          "added.".format(variable, value))

                if actually_do_something():
                    current_diff.append((mode, value))

            # Ensure that only the changes to be saved by the user are applied
            # and removed from later diffs.
            var.value = vdiff.old_value
            var.apply_diff(current_diff)
            args.environment.apply_change(var)

            diff_to_save = var.merge_diff(diff_in_snapshot, current_diff)
            snapshot[variable] = diff_to_save

    # Save the apply_change() results.
    args.environment.save()


def register(argparser, shell):
    if not (shell.is_envprobe_capable and shell.manages_environment_variables):
        return

    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('SNAPSHOT',
                        type=str,
                        help="The name of the snapshot to create or update.")
    parser.add_argument('VARIABLE',
                        type=str,
                        nargs='*',
                        help="Save the values of the specified variable(s), "
                             "e.g. PATH, only.")
    parser.add_argument('-p', '--patch',
                        action='store_true',
                        required=False,
                        help="Interactively prompt and choose which changes "
                             "should be saved.")

    parser.set_defaults(func=command)
