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
from argparse import Namespace
import os
import pytest

from envprobe.commands.set_variable import command
from envprobe.environment import Environment
from envprobe.library import get_variable_information_manager
from envprobe.shell import FakeShell


class FakeShell2(FakeShell):
    @property
    def manages_environment_variables(self):
        return True


class PathHeuristic:
    def __call__(self, name, env=None):
        return 'path' if name == "PATH" else 'string'


@pytest.fixture
def args(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp_path, "cfg")

    shell = FakeShell2()
    envdict = {"PATH": "/Foo:/Bar",
               "FOO": "Foo",
               "NUM": "8"}

    arg = Namespace()
    arg.environment = Environment(shell, envdict, PathHeuristic())

    yield arg


def test_set_description(capfd, args):
    args.VARIABLE = "PATH"
    args.description = "Test"

    configuration = get_variable_information_manager(args.VARIABLE,
                                                     read_only=True)
    assert(configuration[args.VARIABLE] is None)

    command(args)

    stdout, stderr = capfd.readouterr()
    assert("Set description for 'PATH'." in stdout)
    assert(not stderr)

    configuration = get_variable_information_manager(args.VARIABLE,
                                                     read_only=True)
    assert(configuration[args.VARIABLE]["description"] == "Test")
