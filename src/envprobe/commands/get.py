name = 'get'
description = \
    """Print the value of an environment variable in full.

    Alternatively, this command can be accessed by calling
    `envprobe ?VARIABLE`."""
help = "{?VARIABLE} Print the value of an environment variable."


def command(args):
    print(args)


def register(argparser, registered_command_list):
    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('VARIABLE',
                        type=str,
                        help="The variable to access, e.g. EDITOR or PATH.")
    parser.add_argument('-i', "--info",
                        action='store_true',
                        help="Show additional detailed information for the "
                             "variable.")
    parser.set_defaults(func=command)
    registered_command_list.append(name)
