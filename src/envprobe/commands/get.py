import shlex
import sys

from ..vartypes import get_kind
from ..vartypes.array import Array

name = 'get'
description = \
    """Print the value of an environment variable in full.

    Alternatively, this command can be accessed by calling
    `envprobe ?VARIABLE`."""
help = "{?VARIABLE} Print the value of an environment variable."


def command(args):
    try:
        env_var, defined = args.environment[args.VARIABLE]
    except KeyError:
        raise ValueError("This environment variable can not or should not be "
                         "managed through Envprobe.")

    if not defined:
        print("{0} is not defined".format(args.VARIABLE), file=sys.stderr)
        return

    print("{0}={1}".format(env_var.name, shlex.quote(env_var.raw())))

    if args.info:
        if isinstance(env_var, Array):
            print("\n{0}:".format(env_var.name))
            if not len(env_var.value):
                print(" --- empty ---")
            else:
                for e in env_var.value:
                    print("\t{0}".format(e))

        print()
        try:
            print("Type: '{0}'".format(get_kind(type(env_var))))
        except KeyError:
            print("Type: 'unknown' ({0})".format(str(type(env_var))))

        community_data = args.community.get_description(env_var.name)
        description = community_data.get("description", None)
        source = community_data.get("source", None)
        if description:
            print("Description:\n\t{0}".format(description))

            if source:
                print("Source: {0}".format(source))


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
