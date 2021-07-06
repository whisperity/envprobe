"""
Handles user-facing operations related to tweaking the type of variables.
"""
import argparse

import community_descriptions
from configuration import global_config


def __update(args):
    community_descriptions.get_description_release()


def __create_set_type_subcommand(main_parser):
    epilogue = "The following variable type classes are known to Envprobe:\n"

    epilogue += "\nSetting the type to 'ignored' will make Envprobe "       \
                "prohibit access of the variable. (Note: this is not the "  \
                "same as \"track ignoring\" the variable. The latter only " \
                "disables the variable in the save/load command, the "      \
                "'ignored' type disables the get/set too!)"

    epilogue += "\n\nIf you think specifying the type of a variable could "   \
                "benefit other users,\nplease submit us an issue on GitHub: " \
                "http://github.com/whisperity/envprobe-descriptions"

def __create_set_description_subcommand(main_parser):
    parser = main_parser.add_parser(
        epilog="If you think specifying a description for a variable could "
               "benefit other users, please submit us an issue on GitHub: "
               "http://github.com/whisperity/envprobe-descriptions"
    )


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
    __create_update_subcommand(main_parser)
