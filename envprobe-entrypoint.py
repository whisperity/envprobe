#!/usr/bin/env python3

"""
Main entry point for the Envprobe tool. This module handles the parsing of
command-line arguments and dispatching the user's request to the submodules.
"""

import argparse
import sys

from commands import get_common_epilogue_or_die
from commands import envvars as envvars_command
from commands import state as state_command
from shell import *  # Keep this import, this registers the known shells.


def __main():
    """
    Entry point.
    """
    epilogue = get_common_epilogue_or_die()
    parser = argparse.ArgumentParser(
        prog='envprobe',
        description="Envprobe helps you set up your shell environment "
                    "variables in an easy way, with no need of creating and "
                    "editing configuration files and loading them manually.",
        epilog=epilogue
    )
    subparsers = parser.add_subparsers(title="available commands")

    # The ordering of the commands here specifies in which order they are
    # shown on the output!
    envvars_command.create_subcommand_parser(subparsers)
    state_command.create_subcommand_parser(subparsers)

    argv = envvars_command.transform_subcommand_shortcut(sys.argv)
    args = parser.parse_args(argv[1:])  # Cut the shell command's name.
    if 'func' in args:
        try:
            args.func(args)
        except Exception as e:
            print("Cannot execute the specified action.")
            print(str(e))
            import traceback
            traceback.print_exc()
    else:
        print(epilogue)


# Define an entry point so that the tool is usable by calling "./envprobe.py".
if __name__ == "__main__":
    __main()
