"""
Handles the operations related to the saving and loading the user's saved
environments.
"""
import os
import sys

from configuration import global_config
from configuration.tracked_variables import TrackingOverlay
from shell import get_current_shell
from state import create_environment_variable, environment
from state.saved import get_save_folder, Save
from vartypes.array import ArrayEnvVar


def __clean_variable_list(var_list):
    """
    Helper method to clean a list of variable names from user input. Keeps
    only useful (non-empty) elements of the list.
    """
    return list(filter(lambda x: x, var_list))


def __diff(args):
    TYPES = environment.VariableDifferenceType
    shell = get_current_shell()
    tracking = TrackingOverlay(shell)
    env = environment.Environment(shell)
    diffs = env.diff()
    var_names = __clean_variable_list(args.variable)

    for variable_name in sorted(list(diffs.keys())):
        if var_names and variable_name not in var_names:
            continue
        if not var_names and not tracking.is_tracked(variable_name):
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
                      % (diff[1][1], diff[0][1]))
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


def __list(args):
    for _, _, files in os.walk(get_save_folder()):
        for file in sorted(files):
            print(" - %s" % file.replace('.json', ''))


def __load(args):
    def bool_prompt():
        response = False
        user_input = input("Apply this change? (y/N) ").lower()
        if user_input == 'y' or user_input == 'yes':
            response = True
        return response

    shell = get_current_shell()
    tracking = TrackingOverlay(shell)
    env = environment.Environment(shell)
    var_names = __clean_variable_list(args.variable)

    with Save(args.name, read_only=True) as save:
        if save is None:
            print("Error! The save '%s' cannot be opened, perhaps it is "
                  "being modified by another process!" % args.name,
                  file=sys.stderr)
            return
        if len(save) == 0:
            print("The save '%s' does not exist!" % args.name)

        for variable_name in save:
            if var_names and variable_name not in var_names:
                continue
            if not var_names and not tracking.is_tracked(variable_name):
                continue

            # The 'saved' variable is used to update the environment's
            # "saved" state so the loaded change won't be a difference.
            variable_saved = create_environment_variable(variable_name,
                                                         env.saved_env)
            # The 'shell' variable is used to update the actual value the
            # user experiences in the shell. (This distinction is used
            # because there might be changes in the current shell which were
            # never "saved" into the state file or a save.)
            variable_shell = create_environment_variable(variable_name,
                                                         env.current_env)

            if save[variable_name] == Save.UNSET:
                if args.patch or args.dry_run:
                    print("Variable \"%s\" will be unset (from value: '%s')"
                          % (variable_name, variable_shell.value))

                if not args.dry_run and (not args.patch or bool_prompt()):
                    env.apply_change(variable_saved, remove=True)
                    shell.undefine_env_var(variable_shell)

                continue

            # Read the change from the save and apply it to the variable.
            value = save[variable_name]
            current_value = variable_shell.value
            if not isinstance(value, dict):
                # Single variable changes contain the NEW value in the save.
                # For the sake of user communication here, regard a list
                # containing a single string as a single string.
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                if isinstance(current_value, list) and \
                        len(current_value) == 1:
                    current_value = current_value[0]

                if args.patch or args.dry_run:
                    if variable_name not in env.current_env:
                        print("New variable \"%s\" will be set to value: "
                              "'%s'." % (variable_name, value))
                    elif value == current_value:
                        # Don't change something that already has the new
                        # value.
                        continue
                    else:
                        print("Variable \"%s\" will be changed to value: "
                              "'%s' (previous value was: '%s')"
                              % (variable_name, value, current_value))

                if not args.dry_run and (not args.patch or bool_prompt()):
                    variable_saved.value = value
                    variable_shell.value = value
                    env.apply_change(variable_saved)
                    shell.set_env_var(variable_shell)
            else:
                # Complex changes are represented in a dict.
                if not isinstance(variable_saved, ArrayEnvVar) or \
                        not isinstance(variable_saved, ArrayEnvVar):
                    raise TypeError("Cannot apply a complex add/remove "
                                    "change to a variable which is not an "
                                    "array!")

                insert_idx = 0
                for add in value['add']:
                    if add in current_value:
                        # Ignore adding something that is already there.
                        continue

                    if args.patch or args.dry_run:
                        print("In variable \"%s\", the value (component) "
                              "'%s' will be added."
                              % (variable_name, add))
                    if not args.dry_run and (not args.patch or bool_prompt()):
                        variable_saved.insert_at(insert_idx, add)
                        variable_shell.insert_at(insert_idx, add)
                        insert_idx += 1

                        env.apply_change(variable_saved)
                        shell.set_env_var(variable_shell)

                for remove in value['remove']:
                    if remove not in current_value:
                        # Ignore removing something that is not there.
                        continue

                    if args.patch or args.dry_run:
                        print("In variable \"%s\", the value (component) "
                              "'%s' will be removed."
                              % (variable_name, remove))
                    if not args.dry_run and (not args.patch or bool_prompt()):
                        variable_saved.remove_value(remove)
                        variable_shell.remove_value(remove)
                        env.apply_change(variable_saved)
                        shell.set_env_var(variable_shell)

    # After loading, the user's "known" environment has changed, so it has
    # to be flushed.
    env.flush()


def __save(args):
    def bool_prompt():
        response = False
        user_input = input("Save this change? (y/N) ").lower()
        if user_input == 'y' or user_input == 'yes':
            response = True
        return response

    shell = get_current_shell()
    tracking = TrackingOverlay(shell)
    env = environment.Environment(shell)
    diffs = env.diff()
    var_names = __clean_variable_list(args.variable)

    with Save(args.name, read_only=False) as save:
        if save is None:
            print("Error! The save '%s' cannot be opened, perhaps it is "
                  "being modified by another process!" % args.name,
                  file=sys.stderr)
            return

        for variable_name in sorted(list(diffs.keys())):
            if var_names and variable_name not in var_names:
                continue
            if not var_names and not tracking.is_tracked(variable_name):
                continue

            change = diffs[variable_name]
            diff = change.differences

            variable_saved = create_environment_variable(variable_name,
                                                         env.saved_env)

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
                    variable_saved.value = change.new_value
                    env.apply_change(variable_saved)
            elif change.is_unset():
                # If a variable was removed from the environment, it
                # usually doesn't matter what its value was, only the fact
                # that it was removed.
                if args.patch:
                    print("Variable \"%s\" unset (from value: '%s')"
                          % (variable_name, change.old_value))

                if not args.patch or bool_prompt():
                    del save[variable_name]
                    env.apply_change(variable_saved, remove=True)
            elif change.is_simple_change():
                # If the change was a simple change that changed a
                # variable from something to something we are still only
                # interested in the new value. (This is environment
                # variables, not Git!)
                if args.patch:
                    print("Variable \"%s\" changed to value: '%s' "
                          "(previous value was: '%s')"
                          % (variable_name,
                             change.new_value, change.old_value))

                if not args.patch or bool_prompt():
                    save[variable_name] = change.new_value
                    variable_saved.value = change.new_value
                    env.apply_change(variable_saved)
            else:
                if not isinstance(variable_saved, ArrayEnvVar) or \
                        not isinstance(variable_saved, ArrayEnvVar):
                    raise TypeError("Cannot apply a complex add/remove "
                                    "change to a variable which is not an "
                                    "array!")

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

                        if key == 'add':
                            variable_saved.insert_at(0, value)
                        elif key == 'remove':
                            variable_saved.remove_value(value)
                        env.apply_change(variable_saved)

        # Write the named state save file to the disk.
        save.flush()

        # Write the changed current environment's now saved changes to the
        # shell's known state, so changes saved here are no longer shown as
        # diffs.
        env.flush()


def __delete(args):
    with Save(args.name, read_only=False) as save:
        if save is None:
            print("Error! The save '%s' cannot be opened, perhaps it is "
                  "being modified by another process!" % args.name,
                  file=sys.stderr)
            return

        save.delete_file()


def __create_diff_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='diff',
        description="Shows the difference between the previously "
                    "saved/loaded state and the current environment of the "
                    "shell.",
        help="{%%} Show difference of shell vs. previous save/load."
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


def __create_list_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='list',
        description="List the names of saved differences.",
        help="List the names of saved differences."
    )

    parser.set_defaults(func=__list)
    global_config.REGISTERED_COMMANDS.append('list')


def __create_load_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='load',
        description="Load the previously saved differences of environment "
                    "variables from a named save, and apply them to the "
                    "current shell.",
        help="{{NAME} Load differences from a named save and apply them."
    )

    parser.add_argument('name',
                        metavar='NAME',
                        help="The name of the save where difference was "
                             "saved.")

    parser.add_argument('variable',
                        metavar='VARIABLE',
                        nargs='*',
                        help="Load only the difference for the specified "
                             "variable(s).")

    mgroup = parser.add_mutually_exclusive_group()

    mgroup.add_argument('-n', '--dry-run',
                        action='store_true',
                        required=False,
                        help="Show the differences that would be loaded, "
                             "but don't actually change the environment. "
                             "This is useful for inspecting saved states.")

    mgroup.add_argument('-p', '--patch',
                        action='store_true',
                        required=False,
                        help="Interactively choose changes instead of "
                             "automatically applying the full difference.")

    parser.set_defaults(func=__load)
    global_config.REGISTERED_COMMANDS.append('load')


def __create_save_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='save',
        description="Creates or updates a named save which contains a "
                    "difference in environment variables' values. In case "
                    "the specified save already exists, changes for a "
                    "particular variable is overwritten in the save. (To "
                    "completely overwrite a save, 'delete' it first.)",
        help="{}NAME} Save changes in the environment into a named save."
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
                             "automatically saving the full difference.")

    parser.set_defaults(func=__save)
    global_config.REGISTERED_COMMANDS.append('save')


def __create_delete_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='delete',
        description="Delete a previously saved difference of environment "
                    "variables, a named save.",
        help="Delete a named save."
    )

    parser.add_argument('name',
                        metavar='NAME',
                        help="The name of the save which is to be deleted.")

    parser.set_defaults(func=__delete)
    global_config.REGISTERED_COMMANDS.append('delete')


def create_subcommand_parser(main_parser):
    __create_list_subcommand(main_parser)

    if get_current_shell():
        # Only expose these commands of this module if the user is running
        # envprobe in a known valid shell.
        __create_load_subcommand(main_parser)
        __create_diff_subcommand(main_parser)
        __create_save_subcommand(main_parser)

    __create_delete_subcommand(main_parser)
