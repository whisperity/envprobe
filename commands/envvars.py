"""
Handle the operations that query or alter the values of environmental
variables.
"""

import os

from shell import get_current_shell
from vartypes.array import ArrayEnvVar
from vartypes.string import StringEnvVar
from vartypes.path import PathLikeEnvVar

__SHORTCUT_CHARS = {'+': "add",
                    '-': "remove",
                    '?': "get",
                    '!': "set",
                    '=': "set"
                    }


def transform_subcommand_shortcut(argv):
    """
    Envprobe's most important functionality and selling point is the ease of
    operation on getting and setting environmental variables. This is why the
    user having to type `envprobe add PATH /foo/bar` is too verbose. This
    method transforms the given `argv` argument vector (usually
    :function:`sys.argv`) with some common expansions for ease of use.
    """

    if len(argv) < 2 or (len(argv) == 2 and argv[1] in ['-h', '--help']):
        # Don't do anything if the argument vector does not contain at least
        # one subcommand, or if the user is asking for help.
        return argv

    should_translate = False
    command = argv[1]
    if command in __SHORTCUT_CHARS:
        # Sometimes, users might enter "envprobe + PATH /foo/bar" instead of
        # "envprobe +PATH /foo/bar" which is the "expected" usage. Fix up these
        # cases.
        argv = [argv[0],
                command + (argv[2] if len(argv) >= 3 else '')] + argv[3:]
        command = argv[1]
        should_translate = True
    else:
        # Sometimes, users might enter "envprobe PATH + /foo/bar" which
        # should be a shortcut for "envprobe PATH+ /foo/bar".
        if len(argv) >= 3 and argv[2] in __SHORTCUT_CHARS:
            argv = [argv[0], argv[1] + argv[2]] + argv[3:]
            command = argv[1]
            should_translate = True

    if not should_translate and \
            any([command.startswith(c) or command.endswith(c)
                 for c in __SHORTCUT_CHARS]):
        # If no joining of "command letter to variable" was done, the user
        # might have entered the shortcut as originally intended:
        # "envprobe +PATH /foo/bar".
        should_translate = True

    # Expand the letters into their actual command counterparts.
    if not should_translate:
        return argv

    action, variable_name = None, None
    if command[0] in __SHORTCUT_CHARS:
        action = [__SHORTCUT_CHARS[command[0]]]
        variable_name = command[1:]
    elif command[-1] in __SHORTCUT_CHARS:
        if command[-1] == '+':
            # Only "add" is a position-capable action.
            action = [__SHORTCUT_CHARS[command[-1]], '--position', '-1']
        else:
            action = [__SHORTCUT_CHARS[command[-1]]]
        variable_name = command[:-1]

    argv = [argv[0]] + action + [variable_name] + argv[2:]
    return argv


def __create_environment_variable(key):
    """
    Create an :type:`vartypes.EnvVar` instance for the given environment
    variable `key`.
    """

    # TODO: Improve this heuristic, introduce a way for the user to configure.
    if 'PATH' in key:
        # Consider the variable a PATH-like variable.
        print(key + " contains 'PATH', considering it a POSIX path "
              "variable...")
        return PathLikeEnvVar(key, os.environ.get(key, ""))
    else:
        print("Considering " + key + " as a string variable...")
        return StringEnvVar(key, os.environ.get(key, ""))


def __get(args):
    env_var = __create_environment_variable(args.VARIABLE)
    print(env_var.name + "=" + env_var.to_raw_var())


def __add(args):
    env_var = __create_environment_variable(args.VARIABLE)
    if not isinstance(env_var, ArrayEnvVar):
        raise NotImplementedError("'add' and 'remove' operations are only "
                                  "applicable to array-like environmental "
                                  "variables.")

    print(env_var.name + " += " + args.VALUE + " at position " +
          str(args.position))
    env_var.insert_at(args.position, args.VALUE)
    print(env_var.name + "=" + env_var.to_raw_var())


def __remove(args):
    env_var = __create_environment_variable(args.VARIABLE)
    if not isinstance(env_var, ArrayEnvVar):
        raise NotImplementedError("'add' and 'remove' operations are only "
                                  "applicable to array-like environmental "
                                  "variables.")

    print(env_var.name + " -= " + args.VALUE)
    env_var.remove_value(args.VALUE)
    print(env_var.name + "=" + env_var.to_raw_var())


def __set(args):
    print("SET")
    env_var = __create_environment_variable(args.VARIABLE)
    print(env_var.name + " := " + args.VALUE)
    env_var.value = args.VALUE
    print(env_var.name + "=" + env_var.to_raw_var())


def __create_add_subcommand(main_parser):

    parser = main_parser.add_parser(
        name='add',
        description="Add a value to an environmental variable at a given "
                    "position. This command should only be used for "
                    "array-like variables that can contain multiple values, "
                    "such as PATH.",
        help="Add a value to an array-like environmental variable."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable which the value is to be added to, e.g. PATH."
    )

    parser.add_argument(
        'VALUE',
        type=str,
        help="""The value to be added, e.g. "/usr/bin"."""
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


def __create_remove_subcommand(main_parser):

    parser = main_parser.add_parser(
        name='remove',
        description="Remove a value from an environmental variable. This "
                    "command should only be used for array-like variables "
                    "that can contain multiple values, such as PATH.",
        help="Remove a value from an array-like environmental variable."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable which the value is to be removed from, e.g. PATH."
    )

    parser.add_argument(
        'VALUE',
        type=str,
        help="""The value to be removed, e.g. "/usr/bin"."""
    )

    parser.set_defaults(func=__remove)


def __create_get_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='get',
        description="Print the value of an environmental variable.",
        help="Print the value of an environmental variable."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable to alter, e.g. EDITOR."
    )

    parser.set_defaults(func=__get)


def __create_set_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='set',
        description="Set the environmental variable to a given value.",
        help="Set the environmental variable to a given value."
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


def create_subcommand_parser(main_parser):
    if not get_current_shell():
        return

    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_get_subcommand(main_parser)
    __create_set_subcommand(main_parser)
    __create_add_subcommand(main_parser)
    __create_remove_subcommand(main_parser)
