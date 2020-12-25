name = 'set'
description = \
    """Set the value of an environment variable, overwriting the previous
    setting.

    Alternatively, this command can be used as `envprobe VARIABLE=VALUE`
    or `envprobe !VARIABLE VALUE`."""
help = "{VARIABLE=} Set the value of an environment variable."


def command(args):
    try:
        env_var, _ = args.environment[args.VARIABLE]
    except KeyError:
        raise ValueError("This environment variable can not or should not be "
                         "managed through Envprobe.")

    env_var.value = args.VALUE
    args.environment.apply_change(env_var)
    args.shell.set_environment_variable(env_var)


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
