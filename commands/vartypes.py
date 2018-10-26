"""
Handles user-facing operations related to tweaking the type of variables.
"""
import argparse

import community_descriptions
from configuration import global_config
from vartypes import ENVTYPE_NAMES_TO_CLASSES
from vartypes import *  # Force importing of all possible variable types.


def __set_type(args):
    descr = community_descriptions.get_description(args.VARIABLE)
    descr['type'] = args.type if not args.delete else None
    community_descriptions.save_description(args.VARIABLE, descr)


def __set_description(args):
    descr = community_descriptions.get_description(args.VARIABLE)
    descr['description'] = ' '.join(args.DESCRIPTION) \
        if args.DESCRIPTION else None
    community_descriptions.save_description(args.VARIABLE, descr)


def __update(args):
    community_descriptions.get_description_release()


def __create_set_type_subcommand(main_parser):
    epilogue = "The following variable type classes are known to Envprobe:\n"
    for key in sorted(ENVTYPE_NAMES_TO_CLASSES.keys()):
        clazz = ENVTYPE_NAMES_TO_CLASSES[key]
        epilogue += " * %s:  %s\n" % (key, clazz.type_description())

    epilogue += "\nSetting the type to 'ignored' will make Envprobe "       \
                "prohibit access of the variable. (Note: this is not the "  \
                "same as \"track ignoring\" the variable. The latter only " \
                "disables the variable in the save/load command, the "      \
                "'ignored' type disables the get/set too!)"

    epilogue += "\n\nIf you think specifying the type of a variable could "   \
                "benefit other users,\nplease submit us an issue on GitHub: " \
                "http://github.com/whisperity/envprobe-descriptions"

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
                        choices=sorted(ENVTYPE_NAMES_TO_CLASSES.keys()) +
                        ['ignored'],
                        help="Set the variable to the given new type.")

    mgroup.add_argument('-d', '--delete',
                        action='store_true',
                        help="Remove the user preference on the type of "
                             "VARIABLE.")

    parser.set_defaults(func=__set_type)
    global_config.REGISTERED_COMMANDS.append('set-type')


def __create_set_description_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='set-description',
        description="A variable's description can help to understand its "
                    "use. This command can be used to set a local (on your "
                    "user) description for the given VARIABLE.",
        help="Change the local description of a variable.",
        epilog="If you think specifying a description for a variable could "
               "benefit other users, please submit us an issue on GitHub: "
               "http://github.com/whisperity/envprobe-descriptions"
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable name to change the configuration for, e.g. PATH."
    )

    parser.add_argument('DESCRIPTION',
                        nargs='*',
                        help="The description to set. Words of the "
                             "description will be concatenated. For best "
                             "results, specify a single string.")

    parser.set_defaults(func=__set_description)
    global_config.REGISTERED_COMMANDS.append('set-description')


def __create_update_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='update-community',
        description="Check if the \"Envprobe Variable Description Knowledge "
                    "Base\" project has a new version available, and if yes, "
                    "download the data and install the knowledge into the "
                    "user's local system. This subcommand requires Internet "
                    "access.",
        help="Download variable types and descriptions from the Internet.",
        epilog="The knowledgebase project is available at: "
               "http://github.com/whisperity/envprobe-descriptions"
    )

    parser.set_defaults(func=__update)
    global_config.REGISTERED_COMMANDS.append('set-description')


def create_subcommand_parser(main_parser):
    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_set_type_subcommand(main_parser)
    __create_set_description_subcommand(main_parser)
    __create_update_subcommand(main_parser)
