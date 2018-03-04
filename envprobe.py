#!/usr/bin/env python3

"""
Main entry point for the Envprobe tool. This module handles the parsing of
command-line arguments and dispatching the user's request to the submodules.
"""

import argparse
import os
import sys

from commands import shell as shell_command
from commands import envvars as envvars_commands
import shell


def __main():
    """
    Entry point.
    """

    # Check if the user is running a Shell currently or not.
    epilogue = None
    if len(sys.argv) == 1 or \
            (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        current_shell = shell.get_current_shell()
        if current_shell is None:
            epilogue = "You are currently using `envprobe` in a shell that " \
                       "does not have it enabled. Please refer to the "      \
                       "README on how to enable envprobe."

            if len(sys.argv) == 1:
                print("To see what commands `envprobe` can do, specify "
                      "'--help'.",
                      file=sys.stderr)
        elif current_shell is False:
            epilogue = "You are currently using an unknown shell, but " \
                       "your environment claims envprobe is enabled. " \
                       "Stop hacking your variables! :)"
        else:
            epilogue = "You are currently using a '{0}' shell, and envprobe " \
                       "is enabled!".format(current_shell.shell_type)

            if int(os.environ.get('_ENVPROBE', 0)) != 1:
                # If the user is not running the command through an alias,
                # present an error. We don't want users to randomly run
                # envprobe if it is enabled and set up.
                print("You are in an environment where `envprobe` is "
                      "enabled, but you used the command '{0}' to run "
                      "envprobe, instead of `envprobe`."
                      .format(sys.argv[0]),
                      file=sys.stderr)
                sys.exit(2)

    parser = argparse.ArgumentParser(
        prog='envprobe',
        description="Envprobe helps you set up your shell environment "
                    "variables in an easy way, with no need of creating and "
                    "editing configuration files and loading them manually.",
        epilog=epilogue
    )
    subparsers = parser.add_subparsers(title="available commands")

    envvars_commands.create_subcommand_parser(subparsers)
    shell_command.create_subcommand_parser(subparsers)

    argv = envvars_commands.transform_subcommand_shortcut(sys.argv)
    args = parser.parse_args(argv[1:])
    if 'func' in args:
        try:
            args.func(args)
        except Exception as e:
            print("Cannot execute the specified action:")
            print(str(e))
            import traceback
            traceback.print_exc()
    else:
        print(epilogue)


# Define an entry point so that the tool is usable with "./envprobe.py"
if __name__ == "__main__":
    __main()
