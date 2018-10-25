"""
Handle the operations concerning hooking Envprobe into a shell.
"""

from configuration import global_config
from shell.bash import BashShell
from state import environment


def create_subcommand_parser(main_parser):
    parser = main_parser.add_parser(
        name='shell',
        description="This command generates a shell executable code snippet "
                    "that can be used to register envprobe's hooks into the "
                    "shell's environment.",
        help="Generate the necessary hooks to register envprobe into a "
             "shell's environment."
    )

    parser.add_argument(
        'SHELL',
        type=str,
        default='bash',
        choices=['bash'],
        help="The name of the shell system for which the hook code is "
             "generated."
    )

    parser.set_defaults(func=__main)
    global_config.REGISTERED_COMMANDS.append('shell')


def __main(args):
    """
    Entry point for handling generation of shell hooks.
    """

    if args.SHELL == 'bash':
        shell = BashShell()

        if shell.is_envprobe_capable():
            print(shell.get_shell_hook())

            # Create the initial environment and make sure its snapshot is
            # saved.
            state = environment.Environment(shell)
            state.save()
        else:
            print(shell.get_shell_hook_error())
