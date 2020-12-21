name = 'set'
description = \
    """Set the value of an environment variable, overwriting the previous
    setting.

    Alternatively, this command can be used as `envprobe VARIABLE=VALUE`
    or `envprobe !VARIABLE VALUE`."""
help = "{VARIABLE=} Set the value of an environment variable."


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
                        help="The variable to change, e.g. EDITOR or PATH.")
    parser.add_argument('VALUE',
                        type=str,
                        help="The new value to write.")
    parser.set_defaults(func=command)
    registered_command_list.append(name)
