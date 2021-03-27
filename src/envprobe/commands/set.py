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
    args.environment.set_variable(env_var)
    args.shell.set_environment_variable(env_var)


def register(argparser, shell):
    if not (shell.is_envprobe_capable and shell.manages_environment_variables):
        return

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
