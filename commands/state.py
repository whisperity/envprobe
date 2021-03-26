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


def __delete(args):
    with Save(args.name, read_only=False) as save:
        if save is None:
            print("Error! The save '%s' cannot be opened, perhaps it is "
                  "being modified by another process!" % args.name,
                  file=sys.stderr)
            return

        save.delete_file()


def __create_list_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='list',
        description="List the names of saved differences.",
        help="List the names of saved differences."
    )

    parser.set_defaults(func=__list)
    global_config.REGISTERED_COMMANDS.append('list')


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
    __create_delete_subcommand(main_parser)
