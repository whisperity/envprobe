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

from .environment import Environment
from .shell import get_current_shell, FakeShell
from .vartype_heuristics import standard_vartype_pipeline


def get_shell_and_env_always(env_dict=None):
    """Return an :py:class:`environment.Environment` and
    :py:class:`shell.Shell`, no matter what.

    Parameters
    ----------
    env_dict : dict, optional
        The raw mapping of environment variables to their values, as in
        :py:data:`os.environ`.

    Return
    ------
    shell : .shell.Shell
        The shell which use can be deduced from the current environment (by
        calling :py:func:`.shell.get_current_shell`).
        If none such can be deduced, a :py:class:`.shell.FakeShell` is
        returned, which is a **valid** :py:class:`.shell.Shell` subclass that
        tells the client code it is not capable of anything.
    env : .environment.Environment
        The environment associated with the current context and the
        instantiated `Shell`.
    """
    if not env_dict:
        env_dict = os.environ

    try:
        sh = get_current_shell(env_dict)
    except KeyError:
        sh = FakeShell()

    env = Environment(sh, env_dict, standard_vartype_pipeline)

    return sh, env
