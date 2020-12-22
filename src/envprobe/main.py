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
from .config_commands import register_shell_commands

mode_description = \
    """Envprobe is a shell tool that helps you manage your environment
    variables easily. The tool is comprised of multiple "modes" or "facades",
    that have to be selected to access the functionality.

    You should normally NOT see this help message if your shell is configured
    properly."""

main_description = \
    """Envprobe is a shell tool that helps you manage your environment
    variables easily, removing the need of having to write clunky `export`
    sequences, or manual loading of configuration files."""
main_help = \
    """The main mode is responsible for interfacing with the environment
    variables."""
main_epilogue = \
    """TODO: Epilogue goes here. Get from the refactor!"""
main_subcommands_description = \
    """Note that the set of subcommands available is *CONTEXT SENSITIVE*,
    and is based on your current shell and environment setup."""


def __main_mode(argv):
    """
    Implementation of Envprobe's main entry point.
    """
    # Instantiate the "globals" of Envprobe that interface with the env vars.
    shell, env = get_shell_and_env_always(os.environ)

    # Create the command-line user interface.
    parser = argparse.ArgumentParser(
            prog="envprobe",
            description=main_description,
            epilog=main_epilogue
    )
    subparsers = parser.add_subparsers(
            title="available commands",
            description=main_subcommands_description)

    # The order of the commands here also specifies the order they are shown
    # in the user's output!
    registered_commands = []
    register_envvar_commands(subparsers, registered_commands, shell)

    argv = transform_subcommand_shortcut(argv, registered_commands)
    args = parser.parse_args(argv[1:])

    # Inject the loaded state's manager objects into the user's request, so
    # the command handlers can accept them.
    args.envprobe_root = argv[0].replace("/__envprobe", "")
    args.shell = shell
    args.environment = env

    # Execute the desired action.
    if 'func' in args:
        try:
            return args.func(args)
        except Exception as e:
            print("[ERROR] Failed to execute the desired action.",
                  file=sys.stderr)
            print(str(e), file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    else:
        print("Epilogue goes here.")
        argv.append("--help")
        args = parser.parse_args(argv[1:])
        return 0


config_description = \
    """This command in Envprobe handles the configuration of your user-specific
    preferences and the current shell's Envprobe-related settings."""
config_help = \
    """The config mode is responsible for user and shell-specific configuration
    options."""
config_epilogue = \
    """TODO: Something here?"""
config_subcommands_description = \
    """Note that the set of subcommands available is *CONTEXT SENSITIVE*,
    and is based on your current shell and environment setup."""


def __config_mode(argv):
    """
    Implementation of Envprobe's configuration entry point.
    """
    # Instantiate the "globals" of Envprobe that interface with the env vars.
    shell, env = get_shell_and_env_always(os.environ)

    # Create the command-line user interface.
    parser = argparse.ArgumentParser(
            prog="envprobe-config",
            description=main_description,
            epilog=main_epilogue
    )
    subparsers = parser.add_subparsers(
            title="available commands",
            description=main_subcommands_description)

    # The order of the commands here also specifies the order they are shown
    # in the user's output!
    register_shell_commands(subparsers, shell)
    # TODO: tracking
    # TODO: vartypes (community?)

    args = parser.parse_args(argv[1:])

    # Inject the loaded state's manager objects into the user's request, so
    # the command handlers can accept them.
    args.envprobe_root = argv[0].replace("/__envprobe", "")
    args.shell = shell
    args.environment = env

    # Execute the desired action.
    if 'func' in args:
        try:
            return args.func(args)
        except Exception as e:
            print("[ERROR] Failed to execute the desired action.",
                  file=sys.stderr)
            print(str(e), file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    else:
        print("Epilogue goes here.")
        argv.append("--help")
        args = parser.parse_args(argv[1:])
        return 0


def __dispatch_factory(to_fn):
    """
    This function helps in dispatching a call of `envprobe mode args...` as
    `envprobe-mode args...`.
    """
    def __bound_dispatcher(argv):
        """
        This function has already bound the :variable:`to_fn` target, and
        accepts the argument vector from the caller.
        """
        # Cut out the mode variable from the argument vector.
        argv = [argv[0]] + argv[2:]
        return to_fn(argv)

    return __bound_dispatcher


def handle_mode(envprobe_root):
    """
    Parse the first argument to an Envprobe commnad-line invocation and
    dispatch to the appropriate mode handler.
    """
    mode_parser = argparse.ArgumentParser(
            prog="envprobe",
            description=mode_description
    )
    modes = mode_parser.add_subparsers(title="available modes")

    main_mode = modes.add_parser(
            name="main",
            description=main_description,
            help=main_help
    )
    main_mode.set_defaults(func=__dispatch_factory(__main_mode))

    config_mode = modes.add_parser(
            name="config",
            description=config_description,
            help=config_help
    )
    config_mode.set_defaults(func=__dispatch_factory(__config_mode))

    selected_facade = [sys.argv[1]] if len(sys.argv) >= 2 else [""]
    args = mode_parser.parse_args(selected_facade)

    # Normalise the entry point and pass the path to the package on.
    sys.argv[0] = os.path.join(envprobe_root, "__envprobe")
    if 'func' in args:
        return args.func(sys.argv)
