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


name = 'load'
description = \
    """Load a previously saved snapshot of environment variables' values from
    the named snapshot, and apply the changes to the current shell.

    Alternatively, this command can be used as `envprobe {SNAPSHOT`."""
help = "{{SNAPSHOT} Load the values from a named snapshot."


def prompt():
    user_input = input("Load and apply this change? (y/N) ").lower()
    return user_input in ['y', 'yes']


def command(args):
    snapshot = get_snapshot(args.SNAPSHOT, read_only=True)
    variables = set(args.VARIABLE) & set(snapshot.keys()) if args.VARIABLE \
        else set(snapshot.keys())
    if not variables:
        return

    def actually_do_something():
        return not args.dry_run and (not args.patch or prompt())

    for variable in sorted(variables):
        if not args.tracking.is_tracked(variable):
            continue

        # Obtain the variable as it was in the stamped/pristine environment.
        # We use this information to "merge in" changes from the save and then
        # make these changes no longer apply as a diff.
        stamped_var, _ = args.environment.get_stamped_variable(variable)

        # Obtain the variable as it is in the current shell. We use this
        # instance to change the actual value effective for the user.
        var, var_exists = args.environment[variable]

        if snapshot[variable] is snapshot.UNDEFINE:
            print("Variable '{0}' (from value '{1}') will be undefined."
                  .format(variable, var.value))
            if actually_do_something():
                args.environment.apply_change(stamped_var, remove=True)
                args.environment.set_variable(var, remove=True)
                args.shell.unset_environment_variable(var)
        else:
            change_actions = snapshot[variable]
            if not isinstance(change_actions, list):
                # Single variable changes are persisted with only the NEW
                # value stored in the snapshot file. We convert this to a
                # single proper diff action.
                change_actions = [('+', change_actions)]

            # Simulate the application of the changes to the current variable.
            # NOTE: This does not change **anything** in the state of the
            # environment itself!
            simulate_full_application, _ = args.environment[variable]
            simulate_full_application.apply_diff(change_actions)

            # The actual changes the user selected to be applied later.
            diff_to_apply = list()

            if not var_exists:
                print("New variable '{0}' will be created with value '{1}'."
                      .format(variable, simulate_full_application.value))
                if actually_do_something():
                    diff_to_apply = change_actions
            elif simulate_full_application.value == var.value:
                # Do not change something that already has the new value.
                continue
            elif len(change_actions) == 1:
                # The change is a simple change, setting a new value.
                print("Variable '{0}' will be changed from '{1}' to '{2}'."
                      .format(variable, var.value,
                              simulate_full_application.value))
                if actually_do_something():
                    diff_to_apply = change_actions
            else:
                # For more complex changes, the changes have to be handled
                # one by one.
                for mode, value in change_actions:
                    if mode == '=':
                        # Ignore unchanged values. This should not be part of
                        # a real snapshot.
                        continue
                    elif mode == '-':
                        print("For variable '{0}' the element '{1}' will be "
                              "removed.".format(variable, value))
                    elif mode == '+':
                        print("For variable '{0}' the element '{1}' will be "
                              "added.".format(variable, value))

                    if actually_do_something():
                        diff_to_apply.append((mode, value))

                    # The order of actions to apply has to be reversed.
                    # For example, if the diff calls to add "/Foo" and "/Bar"
                    # to the PATH, doing the application in this order would
                    # result in "/Bar" being in the front.
                    diff_to_apply = list(reversed(diff_to_apply))

            # Ensure that the changes loaded by the user are applied to the
            # stamped/pristine state and thus are removed from later diffs.
            if diff_to_apply:
                stamped_var.apply_diff(diff_to_apply)
                var.apply_diff(diff_to_apply)

                args.environment.apply_change(stamped_var)
                args.environment.set_variable(var)
                args.shell.set_environment_variable(var)

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
