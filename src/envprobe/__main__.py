"""
Main entry point for the Envprobe tool when called as a Python module.
This script is responsible for setting up the interaction with the user, and
handling the invocation.
"""
import argparse
import os
import sys

from . import get_shell_and_env_always
from .commands import register_envvar_commands
from .commands.shortcuts import transform_subcommand_shortcut


main_description = \
    """Envprobe is a shell tool that helps you manage your  environment
    variables easily, removing the need of having to write clunky `export`
    sequences, or manual loading of configuration files."""
main_epilogue = \
    """TODO: Epilogue goes here. Get from the refactor!"""
main_subcommands_description = \
    """Note that the set of subcommands available is *CONTEXT SENSITIVE*,
    and is based on your current shell and environment setup."""


def __main():
    """
    Implementation of Envprobe's main entry point.
    """
    # Instantiate the "globals" of Envprobe that interface with the env vars.
    shell, env = get_shell_and_env_always(os.environ)

    # Create the command-line user interface.
    parser = argparse.ArgumentParser(
            prog='envprobe',
            description=main_description,
            epilog=main_epilogue
    )
    subparsers = parser.add_subparsers(
            title="available commands",
            description=main_subcommands_description)

    # The order of the commands here also specifies the order they are shown
    # in the user's output!
    registered_commands = []
    register_envvar_commands(subparsers, registered_commands,
                             shell.is_envprobe_capable())

    argv = transform_subcommand_shortcut(sys.argv, registered_commands)
    args = parser.parse_args(argv[1:])

    # Inject the loaded state's manager objects into the user's request, so
    # the command handlers can accept them.
    args.shell = shell
    args.environment = env

    # Execute the desired action.
    if 'func' in args:
        try:
            args.func(args)
        except Exception as e:
            print("[ERROR] Failed to execute the desired action.",
                  file=sys.stderr)
            print(str(e), file=sys.stderr)
            import traceback
            traceback.print_exc()
    else:
        print("Epilogue goes here.")
        argv.append("--help")
        args = parser.parse_args(argv[1:])


if __name__ == "__main__":
    __main()
