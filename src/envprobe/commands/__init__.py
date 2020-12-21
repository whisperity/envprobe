"""
This package implements the individual user-facing subcommands of envprobe that
are related to interfacing with the environment variables.
"""
from . import add, get, remove, undefine
from . import set as set_command


def register_envvar_commands(argparser, registered_command_list,
                             shell_is_envprobe_capable):
    """
    Registers the commands related to environment variable processing into
    the :package:`argparse` argument parser and the command list given,
    if applicable.
    """
    if not shell_is_envprobe_capable:
        return

    # The order of execution determines the order of commands, so it matters!
    get.register(argparser, registered_command_list)
    set_command.register(argparser, registered_command_list)
    undefine.register(argparser, registered_command_list)
    add.register(argparser, registered_command_list)
    remove.register(argparser, registered_command_list)
