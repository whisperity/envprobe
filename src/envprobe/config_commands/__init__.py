"""This package implements the individual user-facing subcommands for
`envprobe config` that are related to setting the configuration of Envprobe
both on the user and the shell level.
"""
from . import hook


def register_shell_commands(argparser, shell):
    """Registers the commands related to shell management into the."""
    if shell.is_envprobe_capable:
        return

    hook.register(argparser)
