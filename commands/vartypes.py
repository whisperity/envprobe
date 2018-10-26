"""
Handles user-facing operations related to tweaking the type of variables.
"""
import argparse

from configuration import global_config
from configuration.variable_types import VariableTypeMap
from vartypes import ENVTYPE_NAMES_TO_CLASSES
from vartypes import *  # Force importing of all possible variable types.


def __set_type(args):
    with VariableTypeMap() as type_map:
        if args.delete and args.VARIABLE in type_map:
            del type_map[args.VARIABLE]
        else:
            type_map[args.VARIABLE] = args.type

        type_map.flush()


def __create_set_type_subcommand(main_parser):
    epilogue = "The following variable type classes are known to Envprobe:\n"
    for key in sorted(ENVTYPE_NAMES_TO_CLASSES.keys()):
        clazz = ENVTYPE_NAMES_TO_CLASSES[key]
        epilogue += " * %s:  %s\n" % (key, clazz.description())

    epilogue += "\nIf you think specifying the type of a variable could "     \
                "benefit other users,\nplease submit us an issue on GitHub: " \
                "http://github.com/whisperity/envprobe"

    parser = main_parser.add_parser(
        name='set-type',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Each environment variable is mapped to a specific type "
                    "in Envprobe - even though they are all just strings in "
                    "the system. This command is used to specify a user "
                    "preference that a VARIABLE should be a different type "
                    "than what Envprobe automatically deduced.",
        help="Change the preferred type of a variable.",
        epilog=epilogue
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable name to change the configuration for, e.g. PATH."
    )

    mgroup = parser.add_mutually_exclusive_group(required=True)

    mgroup.add_argument('-t', '--type',
                        type=str,
                        choices=sorted(ENVTYPE_NAMES_TO_CLASSES.keys()),
                        help="Set the variable to the given new type.")

    mgroup.add_argument('-d', '--delete',
                        action='store_true',
                        help="Remove the user preference on the type of "
                             "VARIABLE.")

    parser.set_defaults(func=__set_type)
    global_config.REGISTERED_COMMANDS.append('set-type')


def create_subcommand_parser(main_parser):
    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_set_type_subcommand(main_parser)
