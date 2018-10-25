"""
Handles the operations related to the saving and loading the user's saved
environments.
"""
import sys

from configuration import global_config
from shell import get_current_shell
from state import environment
from state.saved import Save


def __diff(args):
    TYPES = environment.VariableDifferenceType

    env = environment.Environment(get_current_shell())
    diffs = env.diff()

    for variable_name in sorted(list(diffs.keys())):
        if args.variable and variable_name not in args.variable:
            continue

        change = diffs[variable_name]
        diff = change.differences
        if args.type == 'normal':
            kind = diffs[variable_name].type
            if kind == TYPES.ADDED:
                kind = '+ Added:'
            elif kind == TYPES.REMOVED:
                kind = '- Removed:'
            elif kind == TYPES.CHANGED:
                kind = '! Modified:'

            print("%s %s" % (kind.ljust(11), variable_name))
            if change.is_new() or change.is_unset():
                # If only a remove or an addition took place, show the
                # new value.
                print("     value: %s" % diff[0][1])
            elif change.is_simple_change():
                # If the difference is exactly a single change from a
                # value to another, just show the change.
                print("      from: %s\n        to: %s"
                      % (diff[0][1], diff[1][1]))
            else:
                for action, value in diff:
                    if action == ' ':
                        # Do not show "keep" or "unchanged" lines.
                        continue
                    elif action == '+':
                        print("      added %s" % value)
                    elif action == '-':
                        print("    removed %s" % value)

            print()
        elif args.type == 'unified':
            old_name, new_name = variable_name, variable_name
            old_start, old_count, new_start, new_count = \
                1, len(diff), 1, len(diff)

            if diffs[variable_name].type == TYPES.ADDED:
                old_name = '(new variable)'
                old_start, old_count = 0, 0
            elif diffs[variable_name].type == TYPES.REMOVED:
                new_name = '(variable unset)'
                new_start, new_count = 0, 0

            print("--- %s" % old_name)
            print("+++ %s" % new_name)
            print("@@ -%d,%d +%d,%d @@"
                  % (old_start, old_count, new_start, new_count))
            for difference in diff:
                print("%s %s" % difference)
            print()


def __save(args):
    def bool_prompt():
        response = False
        user_input = input("Save this change? (y/N) ").lower()
        if user_input == 'y' or user_input == 'yes':
            response = True
        return response

    TYPES = environment.VariableDifferenceType

    env = environment.Environment(get_current_shell())
    diffs = env.diff()

    with Save(args.name, read_only=False) as save:
        if save is None:
            print("Error! The save '%s' cannot be opened, perhaps it is "
                  "being modified by another process!" % args.name,
                  file=sys.stderr)
            return

        for variable_name in sorted(list(diffs.keys())):
            if args.variable and variable_name not in args.variable:
                continue

            change = diffs[variable_name]
            diff = change.differences

            # First, transform the change to something that can later be
            # applied.
            if change.is_new():
                # In case a new variable was introduced, we only care
                # about the new, set value.
                if args.patch:
                    print("Variable \"%s\" set to value: '%s'."
                          % (variable_name, change.new_value))

                if not args.patch or bool_prompt():
                    save[variable_name] = change.new_value
            elif change.is_unset():
                # If a variable was removed from the environment, it
                # usually doesn't matter what its value was, only the fact
                # that it was removed.
                if args.patch:
                    print("Variable \"%s\" unset (from value: '%s')"
                          % (variable_name, change.old_value))

                if not args.patch or bool_prompt():
                    del save[variable_name]
            elif change.is_simple_change():
                # If the change was a simple change that changed a
                # variable from something to something we are still only
                # interested in the new value. (This is environment
                # variables, not Git!)
                if args.patch:
                    print("Variable \"%s\" changed to value: '%s', "
                          "(previous value was: '%s')"
                          % (variable_name,
                             change.new_value, change.old_value))

                if not args.patch or bool_prompt():
                    save[variable_name] = change.new_value
            else:
                # For complex changes, such as removal and addition of
                # multiple PATHs, both differences must be saved. This
                # ensures that if a user's particular save depends on
                # something that's usually seen is to not be seen, we can
                # handle it.
                # (In most cases, people only append new values to their
                # various PATHs...)
                save[variable_name] = {'add': [],
                                       'remove': []}

                for mode, value in diff:
                    key = None
                    passive = None
                    if mode == ' ':
                        # Ignore unchanged values.
                        continue
                    elif mode == '+':
                        key = 'add'
                        passive = "added"
                    elif mode == '-':
                        key = 'remove'
                        passive = "removed"

                    if args.patch:
                        print("In variable \"%s\", the value (component) "
                              "'%s' was %s."
                              % (variable_name, value, passive))
                    if not args.patch or bool_prompt():
                        save[variable_name][key].append(value)

        save.flush()


def __create_diff_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='diff',
        description="Shows the difference between the previously "
                    "saved/loaded state and the current environment of the "
                    "shell.",
        help="Show difference of shell vs. previous save/load."
    )

    parser.add_argument('variable',
                        metavar='VARIABLE',
                        nargs='*',
                        help="Show only the difference for the specified "
                             "variable(s).")

    format = parser.add_argument_group("formatting arguments")
    format = format.add_mutually_exclusive_group()

    format.add_argument('-n', '--normal',
                        dest='type',
                        action='store_const',
                        const='normal',
                        help="Show a \"normal\", human-readable difference.")

    format.add_argument('-u', '--unified',
                        dest='type',
                        action='store_const',
                        const='unified',
                        help="Show a unified diff (like calling `diff -u`) "
                             "which can be machine-read.")

    parser.set_defaults(func=__diff,
                        type="normal")
    global_config.REGISTERED_COMMANDS.append('diff')


def __create_save_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='save',
        description="Creates or updates a named save which contains a "
                    "difference in environment variables' values. In case "
                    "the specified save already exists, changes for a "
                    "particular variable is overwritten in the save. (To "
                    "completely overwrite a save, 'delete' it first.)",
        help="Save changes in the environment into a named save."
    )

    parser.add_argument('name',
                        metavar='NAME',
                        help="The name of the save where difference is "
                             "saved.")

    parser.add_argument('variable',
                        metavar='VARIABLE',
                        nargs='*',
                        help="Save only the difference for the specified "
                             "variable(s).")

    parser.add_argument('-p', '--patch',
                        action='store_true',
                        required=False,
                        help="Interactively choose changes instead of "
                             "automatically accepting the full difference.")

    parser.set_defaults(func=__save)
    global_config.REGISTERED_COMMANDS.append('save')


def create_subcommand_parser(main_parser):
    if not get_current_shell():
        return

    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_diff_subcommand(main_parser)
    __create_save_subcommand(main_parser)
