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

from envprobe.commands.save import command
from envprobe.environment import Environment
from envprobe.library import get_snapshot
from envprobe.shell import FakeShell


class MockTracking:
    def __init__(self):
        self.ignored = set()

    def _ignore(self, variable_name):
        self.ignored.add(variable_name)

    def is_tracked(self, variable_name):
        return variable_name not in self.ignored


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
    arg.shell = shell
    arg.tracking = MockTracking()
    arg.patch = False

    # Make some changes.
    arg.environment.stamp()

    path_var, _ = arg.environment["PATH"]
    path_var.value = "/Foo:/Baz"
    arg.environment.set_variable(path_var)

    foo_var, _ = arg.environment["FOO"]
    foo_var.value = "Bar"
    arg.environment.set_variable(foo_var)

    num_var, _ = arg.environment["NUM"]
    arg.environment.set_variable(num_var, remove=True)

    new_var, _ = arg.environment["NEW_VAR"]
    new_var.value = "Something new!"
    arg.environment.set_variable(new_var)

    yield arg


def test_save(capfd, args):
    args.VARIABLE = None
    args.SNAPSHOT = "test_save"
    command(args)

    stdout, stderr = capfd.readouterr()
    expected = ["Variable 'FOO' changed from 'Foo' to 'Bar'.",
                "New variable 'NEW_VAR' with value 'Something new!'.",
                "Variable 'NUM' (from value '8') undefined.",
                "For variable 'PATH' the element '/Bar' was removed.",
                "For variable 'PATH' the element '/Baz' was added."
                ]

    assert(list(filter(lambda x: x, stdout.split('\n'))) == expected)
    assert(not stderr)

    snapshot = get_snapshot(args.SNAPSHOT, read_only=True)
    assert(snapshot["FOO"] == "Bar")
    assert(snapshot["NEW_VAR"] == "Something new!")
    assert(snapshot["NUM"] is snapshot.UNDEFINE)
    assert(snapshot["PATH"] == [('-', "/Bar"), ('+', "/Baz")])


def test_save_definition_overwrite(capfd, args):
    args.VARIABLE = ["NEW_VAR"]
    args.SNAPSHOT = "test_overwrite"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(list(filter(lambda x: x, stdout.split('\n'))) ==
           ["New variable 'NEW_VAR' with value 'Something new!'."])
    assert(not stderr)

    new_var, _ = args.environment["NEW_VAR"]
    args.environment.set_variable(new_var, remove=True)
    # Simulate the environment loading anew, without NEW_VAR being present.
    args.environment.stamp()

    new_var.value = "Another"
    args.environment.set_variable(new_var)

    command(args)
    stdout, stderr = capfd.readouterr()
    assert(list(filter(lambda x: x, stdout.split('\n'))) ==
           ["New variable 'NEW_VAR' with value 'Another'."])
    assert(not stderr)

    snapshot = get_snapshot(args.SNAPSHOT, read_only=True)
    assert(snapshot["NEW_VAR"] == "Another")
