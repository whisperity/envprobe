#!/usr/bin/env python3

"""
Main entry point for the Envprobe tool. This module handles the parsing of
command-line arguments and dispatching the user's request to the submodules.
"""
import argparse
import os
import sys

from commands import shell as shell_command
from shell import Shell
from shell.bash import BashShell


def __shell(args):
    """
    Entry point for handling generation of shell hooks.
    """

    if args.SHELL == 'bash':
        shell = BashShell()

        if shell.is_envprobe_capable():
            print(shell.get_shell_hook())
        else:
            print(shell.get_shell_hook_error())


def __main():
    """
    Entry point.
    """

    # Check if the user is running a Shell currently or not.
    epilogue=None
    if len(sys.argv) == 1 or \
            (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        shell_type = os.environ.get('ENVPROBE_SHELL_TYPE')
        if not shell_type:
            epilogue = "You are currently using `envprobe` in a shell that " \
                       "does not have it enabled. Please refer to the "      \
                       "README on how to enable envprobe."

            if len(sys.argv) == 1:
                print("To see what commands `envprobe` can do, specify "
                      "'--help'.",
                      file=sys.stderr)
        else:
            current_shell = Shell.get_current_shell(shell_type)
            if current_shell:
                epilogue = "You are currently using a '{0}' shell, " \
                           "and envprobe is enabled!" \
                    .format(current_shell.shell_type)

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
            else:
                epilogue = "You are currently using an unknown shell, but " \
                           "your environment claims envprobe is enabled. "  \
                           "Stop hacking your variables! :)"

    parser = argparse.ArgumentParser(
        prog='envprobe',
        description="Envprobe helps you set up your shell environment "
                    "variables in an easy way, with no need of creating and "
                    "editing configuration files and loading them manually.",
        epilog=epilogue
    )
    subparsers = parser.add_subparsers(title="available commands")

    shell_command.create_subcommand_parser(subparsers, __shell)

    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        print(epilogue)


# Define an entry point so that the tool is usable with "./envprobe.py"
if __name__ == "__main__":
    __main()
