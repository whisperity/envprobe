"""
Handle the operations that query or alter the values of environmental
variables.
"""

import community_descriptions
from configuration import global_config
from shell import get_current_shell
from state import create_environment_variable
from vartypes import ENVTYPE_CLASSES_TO_NAMES
from vartypes.array import ArrayEnvVar


def __get(args):
    env_var = create_environment_variable(args.VARIABLE)
    if env_var is None:
        raise ValueError("This environment variable cannot or should not "
                         "be managed.")
    print(env_var.name + "=" + env_var.to_raw_var())

    if isinstance(env_var, ArrayEnvVar):
        print(env_var.name + ":")
        if len(env_var.value) == 0:
            print("  (empty)")
        else:
            for val in env_var.value:
                print("  " + val)

    if args.info:
        print()
        print("Type: '%s'" % ENVTYPE_CLASSES_TO_NAMES[type(env_var)])
        descr = community_descriptions.get_description(args.VARIABLE)

        description = descr.get('description', None)
        if description:
            print("Description:")
            print("  " + description)

        source = descr.get('source', None)
        if source:
            print("Source: %s" % source)


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


def __set(args):
    env_var = create_environment_variable(args.VARIABLE)
    if env_var is None:
        raise ValueError("This environment variable cannot or should not "
                         "be managed.")
    env_var.value = args.VALUE
    get_current_shell().set_env_var(env_var)


def __undefine(args):
    env_var = create_environment_variable(args.VARIABLE)
    if env_var is None:
        raise ValueError("This environment variable cannot or should not "
                         "be managed.")
    get_current_shell().undefine_env_var(env_var)


def create_subcommand_parser(main_parser):
    if not get_current_shell():
        return
