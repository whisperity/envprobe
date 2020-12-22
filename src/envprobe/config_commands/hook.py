"""
Handles the operation concerning of hooking Envprobe into a shell.
"""
import tempfile

from ..environment import Environment
from ..shell import load, load_all, get_known_kinds

name = 'hook'
description = \
    """Generate the shell-executable code snippet that is used to register
    Envprobe's controlling hooks into the current shell.
    Running of this command is necessary to have Envprobe be able to interface
    with the session.

    The result of a successful run is a shell-specific script on the standard
    output, which must be evaluated (by calling `eval`, usually) inside the
    current shell's scope, and not in a subshell."""
help = "Generate the hooks and register Envprobe into the shell."


def command(args):
    # Generate a temporary directory where the running shell's data will be
    # persisted.
    tempd = tempfile.mkdtemp(prefix=".envprobe.{0}-".format(args.PID))
    shell = load(args.SHELL)(args.PID, tempd)

    # Create the initial environment dump in the persisted storage.
    environment = Environment(shell)
    environment.stamp()
    environment.save()

    print(shell.get_shell_hook(args.envprobe_root))


def register(argparser):
    load_all()  # Retrieve all shells from the module so we have them.

    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('SHELL',
                        type=str,
                        choices=get_known_kinds(),
                        help="The variable to access, e.g. EDITOR or PATH.")
    parser.add_argument('PID',
                        type=int,
                        help="The process ID (PID) of the running shell "
                             "process.")
    parser.set_defaults(func=command)
