# Copyright (C) 2018 Whisperity
#
# SPDX-License-Identifier: GPL-3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import stat
import tempfile

from envprobe.environment import Environment
from envprobe.settings import get_runtime_directory
from envprobe.shell import load, load_all, get_known_kinds


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
    rtdir = get_runtime_directory(os.getuid())
    dir_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    os.makedirs(rtdir, dir_mode, exist_ok=True)

    tempd = tempfile.mkdtemp(prefix="{0}-".format(args.PID), dir=rtdir)
    shell = load(args.SHELL)(args.PID, tempd)

    # Create the initial environment dump in the persisted storage for the
    # now instantiated shell.
    environment = Environment(shell,
                              # Use the environment the 'hook' command was
                              # called with.
                              args.environment.current_environment,
                              args.environment.type_heuristics)
    environment.stamp()
    environment.save()

    print(shell.get_shell_hook(args.envprobe_root))


def register(argparser, shell):
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
