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


def __create_add_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='add',
        description="Add a value to an environmental variable at a given "
                    "position. This command should only be used for "
                    "array-like variables that can contain multiple values, "
                    "such as PATH. Alternatively, this command can be used "
                    "as `envprobe +VARIABLE value1 value2 ...`.",
        help="{+VARIABLE VALUE} Add values to an array-like environmental "
             "variable."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable which the value is to be added to, e.g. PATH."
    )

    parser.add_argument(
        'VALUE',
        type=str,
        nargs='+',
        help="""The values to be added, e.g. "/usr/bin". Values are added """
             """in the order specified."""
    )

    parser.add_argument(
        '--position',
        type=int,
        required=False,
        default=0,
        help="The position in the environmental variable where the value "
             "should be added at. This is either a positive index from the "
             "beginning of the list, or a negative index which is an element "
             "backwards from the end of the list. The first element's index "
             "is 0, the last element's is -1. The value will be added AT the "
             "position given, shifting every element AFTER the new one to the "
             "right by one."
    )

    parser.set_defaults(func=__add)
    global_config.REGISTERED_COMMANDS.append('add')


def __create_remove_subcommand(main_parser):

    parser = main_parser.add_parser(
        name='remove',
        description="Remove a value from an environmental variable. This "
                    "command should only be used for array-like variables "
                    "that can contain multiple values, such as PATH. "
                    "Alternatively, this command can be used as `envprobe "
                    "-VARIABLE value1 value2 ...`.",
        help="{-VARIABLE VALUE} Remove values from an array-like "
             "environmental variable."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable which the value is to be removed from, e.g. PATH."
    )

    parser.add_argument(
        'VALUE',
        type=str,
        nargs='+',
        help="""The values to be removed, e.g. "/usr/bin"."""
    )

    parser.set_defaults(func=__remove)
    global_config.REGISTERED_COMMANDS.append('remove')


def __create_get_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='get',
        description="Print the value of an environmental variable. "
                    "Alternatively, this command can be used as `envprobe "
                    "?VARIABLE`.",
        help="{?VARIABLE} Print the value of an environmental variable."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable to alter, e.g. EDITOR."
    )

    parser.add_argument('-i', '--info', '-d', '--details',
                        action='store_true',
                        help="Show additional information for the variable.")

    parser.set_defaults(func=__get)
    global_config.REGISTERED_COMMANDS.append('get')


def __create_set_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='set',
        description="Set the environmental variable to a given value. "
                    "Alternatively, this command can be used as `envprobe "
                    "VARIABLE=VALUE` or `envprobe ! VARIABLE VALUE`.",
        help="{VARIABLE=VALUE} Set the environmental variable to a given "
             "value."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable to alter, e.g. EDITOR."
    )

    parser.add_argument(
        'VALUE',
        type=str,
        help="The value to set the environmental variable to."
    )

    parser.set_defaults(func=__set)
    global_config.REGISTERED_COMMANDS.append('set')


def __create_undefine_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='undefine',
        description="Unsets the given environment variable, undefining its "
                    "value.",
        help="{^VARIABLE} Undefine an environmental variable."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable to undefine, e.g. EDITOR."
    )

    parser.set_defaults(func=__undefine)
    global_config.REGISTERED_COMMANDS.append('undefine')


def create_subcommand_parser(main_parser):
    if not get_current_shell():
        return

    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_get_subcommand(main_parser)
    __create_set_subcommand(main_parser)
    __create_add_subcommand(main_parser)
    __create_remove_subcommand(main_parser)
    __create_undefine_subcommand(main_parser)
