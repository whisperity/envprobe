"""
Handles the operations related to the saving and loading the user's saved
environments.
"""

from configuration import global_config
from shell import get_current_shell
from state import environment


def __diff(args):

    # print(args)
    x = environment.Environment(get_current_shell())
    import json
    # print(json.dumps(x.current_env, indent=4))

    diff = x.diff()
    for k in sorted(list(diff.keys())):
        print(json.dumps(diff[k].dict(), indent=4))


def __create_diff_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='diff',
        description="Shows the difference between the previously "
                    "saved/loaded state and the current environment of the "
                    "shell.",
        help="Show difference of shell vs. previous save/load."
    )

    parser.set_defaults(func=__diff)
    global_config.REGISTERED_COMMANDS.append('diff')


def create_subcommand_parser(main_parser):
    if not get_current_shell():
        return

    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_diff_subcommand(main_parser)
