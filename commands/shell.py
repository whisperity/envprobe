"""

"""


def create_subcommand_parser(main_parser, func):
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

    parser.set_defaults(func=func)
