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
"""Implements a logic that maps shortcut calls of envprobe (such as "ep A=b")
to expanded command invocations.
"""

# Map certain shortcut characters to different actual commands.
__SHORTCUT_CHARS = {'+': "add",
                    '-': "remove",
                    '?': "get",
                    '!': "set",
                    '=': "set",
                    '^': "undefine",
                    '{': "load",  # < would be interpreted by shell. :(
                    '}': "save",  # > would be interpreted by shell. :(
                    '%': "diff",
                    }


def transform_subcommand_shortcut(argv, registered_commands):
    """Transforms the `argv` invocation with potential shortcut characters to
    a full invocation.

    Envprobe's most important functionality and selling point is the ease of
    operation on getting and setting environmental variables. This is why the
    user having to type `envprobe add PATH /foo/bar` is too verbose. This
    method transforms the given `argv` argument vector (usually
    :function:`sys.argv`) with some common expansions for ease of use.

    Parameters
    ----------
    registered_comamnds : list(str)
        The names of commands that are loaded and registered into the system.
        Any invocation in the form of `ep set` (if `set` is in
        `registered_commands`) will resolve to the command itself, as opposed
        to considering `set` as the variable name.
    """

    if len(argv) < 2 or (len(argv) == 2 and argv[1] in ['-h', '--help']):
        # Don't do anything if the argument vector does not contain at least
        # one subcommand, or if the user is asking for help.
        return argv

    should_translate = False
    command = argv[1]

    if command in __SHORTCUT_CHARS:
        # Sometimes, users might enter "envprobe + PATH /foo/bar" instead of
        # "envprobe +PATH /foo/bar" which is the "expected" usage. Fix up these
        # cases.
        argv = [argv[0],
                command + (argv[2] if len(argv) >= 3 else '')] + argv[3:]
        command = argv[1]
        should_translate = True
    else:
        # Sometimes, users might enter "envprobe PATH + /foo/bar" which
        # should be a shortcut for "envprobe PATH+ /foo/bar".
        if len(argv) >= 3 and argv[2] in __SHORTCUT_CHARS:
            argv = [argv[0], argv[1] + argv[2]] + argv[3:]
            command = argv[1]
            should_translate = True

    if len(argv) == 2 and '=' in command:
        # If the user says "envprobe VAR=VAL", understand it as "envprobe
        # VAR= VAL" which will be translated into a setter action.
        parts = command.split('=')
        variable_name, value = parts[0], parts[1]
        argv = [argv[0], 'set', variable_name, value]

    if not should_translate and \
            any([command.startswith(c) or command.endswith(c)
                 for c in __SHORTCUT_CHARS]):
        # If no joining of "command letter to variable" was done, the user
        # might have entered the shortcut as originally "intended":
        # "envprobe +PATH /foo/bar".
        should_translate = True
    elif len(argv) == 2 and command not in registered_commands \
            and not any([command.startswith(c) or command.endswith(c)
                         for c in __SHORTCUT_CHARS]):
        # Shortcut "envprobe PATH" to "envprobe get PATH", if a seemingly
        # valid variable name (not colliding with a normal command of envprobe)
        # is given.
        argv = [argv[0], 'get', command]

    if not should_translate:
        return list(map(lambda s: s.strip(), argv))

    # Expand the letters into their actual command counterparts.
    action, variable_name = None, None
    if command[0] in __SHORTCUT_CHARS:
        action = [__SHORTCUT_CHARS[command[0]]]
        variable_name = command[1:]
    elif command[-1] in __SHORTCUT_CHARS:
        if command[-1] == '+':
            # Only "add" is a position-capable action, in which case the '+'
            # at the end mean suffix, and at the beginning means prefix.
            action = [__SHORTCUT_CHARS[command[-1]], '--position', '-1']
        else:
            action = [__SHORTCUT_CHARS[command[-1]]]
        variable_name = command[:-1]

    if len(argv) == 4 and (
            (argv[2] == '' and argv[3] == variable_name) or
            (argv[2] == variable_name and argv[3] == '')):
        # If the users enter 'ep VAR=""' the variable name would get
        # duplicated below, so we change it to the entered empty string.
        argv = argv[:2] + ['']

    # Cut out the empty parts from the translated argv, thus forbidding simply
    # saying "envprobe ?" or "envprobe =" by itself.
    old_argv_tail = argv[2:]
    argv = [argv[0]] + action
    if variable_name:
        argv.append(variable_name)
    for e in filter(lambda x: x, old_argv_tail):  # x is truthy
        argv.append(e)

    return list(map(lambda s: s.strip(), argv))
