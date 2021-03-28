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
import shutil


name = 'consume'
description = \
    """Print and consume the Envprobe control script for the shell.
    This command will emit the shell-specific script that, when evaluated
    (by calling `eval`, usually) inside the current shell's scope will set the
    environment variables **in the shell** to the value the user intended.

    This command should rarely be used by end-users directly.
    """
help = "Obtain the shell code for setting the variables to requested values."


def command(args):
    try:
        with open(args.shell.control_file, 'r+') as f:
            contents = f.read()
            if contents:
                print("# --- Envprobe hook begin ---")
                print(contents)
                print("# --- Envprobe hook end ---")
                f.truncate(0)
    except FileNotFoundError:
        # Not a problem if the file doesn't exist yet.
        pass

    if args.detach:
        shutil.rmtree(args.shell.configuration_directory, ignore_errors=True)
        print(args.shell.get_shell_unhook())


def register(argparser, shell):
    if not shell.is_envprobe_capable:
        return

    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('-d', '--detach',
                        action='store_true',
                        help="If specified, the shellcode will contain "
                             "instructions for unloading Envprobe from the "
                             "current shell. The backing structures which "
                             "make Envprobe run will be removed from the "
                             "filesystem, and thus Envprobe will not be able "
                             "to run until a new `hook` call is made. "
                             "WARNING: If '--detach' is given, there is "
                             "**NO** going back!")
    parser.set_defaults(func=command)
