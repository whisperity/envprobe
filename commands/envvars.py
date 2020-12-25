"""
Handle the operations that query or alter the values of environmental
variables.
"""
from shell import get_current_shell
from state import create_environment_variable
from vartypes.array import ArrayEnvVar


def __add(args):
    env_var = create_environment_variable(args.VARIABLE)
    if env_var is None:
        raise ValueError("This environment variable cannot or should not "
                         "be managed.")
    if not isinstance(env_var, ArrayEnvVar):
        raise NotImplementedError("'add' and 'remove' operations are only "
                                  "applicable to array-like environmental "
                                  "variables.")

    for val in args.VALUE:
        env_var.insert_at(args.position, val)
        if args.position >= 0:
            # If the arguments are appended with a positive index, we insert
            # the values in order. If the arguments are inserted at a negative
            # index, the position must not be modified, because the arguments
            # get shifted with the insert.
            args.position += 1
    get_current_shell().set_env_var(env_var)


def __remove(args):
    env_var = create_environment_variable(args.VARIABLE)
    if env_var is None:
        raise ValueError("This environment variable cannot or should not "
                         "be managed.")
    if not isinstance(env_var, ArrayEnvVar):
        raise NotImplementedError("'add' and 'remove' operations are only "
                                  "applicable to array-like environmental "
                                  "variables.")

    for val in args.VALUE:
        env_var.remove_value(val)
    get_current_shell().set_env_var(env_var)


def create_subcommand_parser(main_parser):
    if not get_current_shell():
        return
