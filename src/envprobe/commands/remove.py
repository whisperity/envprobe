name = 'remove'
description = \
    """"Remove element value(s) from an environment variable.
    This command may only be used for array variables, such as PATH.


    Alternatively, this command can be accessed by calling
    envprobe -VARIABLE value1 value2 ...`."""
help = "{-VARIABLE} Remove element(s) from an array variable."


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
                        help="The variable which the value(s) will be removed "
                             "from, e.g. PATH.")
    parser.add_argument('VALUE',
                        type=str,
                        nargs='+',
                        help="The value(s) to be removed, e.g. \"/usr/bin\". "
                             "All occurrences of the specified values will "
                             "be removed, and the list may contain "
                             "duplicates.")
    parser.set_defaults(func=command)
    registered_command_list.append(name)
