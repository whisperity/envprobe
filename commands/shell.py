"""
Handle the operations concerning hooking Envprobe into a shell.
"""

from shell.bash import BashShell


def create_subcommand_parser(main_parser):
    parser = main_parser.add_parser(
        name='shell',
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


def __main(args):
    """
    Entry point for handling generation of shell hooks.
    """

    if args.SHELL == 'bash':
        shell = BashShell()

        if shell.is_envprobe_capable():
            print(shell.get_shell_hook())
        else:
            print(shell.get_shell_hook_error())
