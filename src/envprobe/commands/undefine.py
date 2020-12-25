name = 'undefine'
description = \
    """Unsets the environment variable, making it behave as if it was not
    defined.
    (In some cases, there are subtle differences between a variable
    defined to empty string, or not being defined. In other cases, the
    two are considered equivalent.

    Alternatively, this command can be accessed by calling
    `envprobe ^VARIABLE`."""
help = "{^VARIABLE} Undefine an environment variable."


def command(args):
    try:
        env_var, defined = args.environment[args.VARIABLE]
    except KeyError:
        raise ValueError("This environment variable can not or should not be "
                         "managed through Envprobe.")

    if not defined:
        return

    args.environment.set_variable(env_var, remove=True)
    args.shell.unset_environment_variable(env_var)


def register(argparser, registered_command_list):
    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('VARIABLE',
                        type=str,
                        help="The variable to undefine, e.g. EDITOR. "
                             "(Note: We do *NOT* recommend undefining PATH!)")
    parser.set_defaults(func=command)
    registered_command_list.append(name)
