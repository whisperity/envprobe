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

from envprobe.commands.load import command
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

    def _set_environment_variable(self, env_var):
        pass

    def _unset_environment_variable(self, env_var):
        pass


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
    arg.dry_run = False
    arg.patch = False

    arg.environment.stamp()  # Simulate a clean start with some state.

    # Save some changes into a snapshot.
    snapshot = get_snapshot("test_save", read_only=False)
    snapshot["PATH"] = [('-', "/Bar"), ('+', "/Baz")]
    snapshot["FOO"] = "Bar"
    del snapshot["NUM"]
    snapshot["NEW_VAR"] = "Something new!"

    yield arg


def test_load(capfd, args):
    args.VARIABLE = None
    args.SNAPSHOT = "test_save"
    command(args)

    stdout, stderr = capfd.readouterr()
    expected = ["Variable 'FOO' will be changed from 'Foo' to 'Bar'.",
                "New variable 'NEW_VAR' will be created with value "
                "'Something new!'.",
                "Variable 'NUM' (from value '8') will be undefined.",
                "For variable 'PATH' the element '/Bar' will be removed.",
                "For variable 'PATH' the element '/Baz' will be added."
                ]

    assert(list(filter(lambda x: x, stdout.split('\n'))) == expected)
    assert(not stderr)

    assert(args.environment["FOO"][0].value == "Bar")
    assert(args.environment["NEW_VAR"][1])
    assert(not args.environment["NUM"][1])
    assert("/Foo" in args.environment["PATH"][0].value)
    assert("/Bar" not in args.environment["PATH"][0].value)
    assert("/Baz" in args.environment["PATH"][0].value)

    assert(args.environment.get_stamped_variable("FOO")[0].value == "Bar")
    assert(args.environment.get_stamped_variable("NEW_VAR")[1])
    assert(not args.environment.get_stamped_variable("NUM")[1])
    assert("/Foo" in args.environment.get_stamped_variable("PATH")[0].value)
    assert("/Bar" not in args.environment.get_stamped_variable("PATH")[0]
           .value)
    assert("/Baz" in args.environment.get_stamped_variable("PATH")[0].value)

    assert(not args.environment.diff())


def test_save_tracking(capfd, args):
    args.tracking._ignore("FOO")
    args.tracking._ignore("NEW_VAR")
    args.tracking._ignore("NUM")
    args.tracking._ignore("PATH")

    args.VARIABLE = None
    args.SNAPSHOT = "test_save"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(not args.environment.diff())


def test_load_with_nonstamped_changes_overwrite(capfd, args):
    new_var, _ = args.environment["NEW_VAR"]
    new_var.value = "NonSaved Change!"
    args.environment.set_variable(new_var)

    args.VARIABLE = ["NEW_VAR"]
    args.SNAPSHOT = "test_save"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(list(filter(lambda x: x, stdout.split('\n'))) ==
           ["Variable 'NEW_VAR' will be changed from 'NonSaved Change!' to "
            "'Something new!'."])
    assert(not stderr)

    assert(args.environment["NEW_VAR"][0].value == "Something new!")
    assert(args.environment.get_stamped_variable("NEW_VAR")[0].value ==
           "Something new!")

    assert(not args.environment.diff())


def test_load_with_nonstamped_changes_append(capfd, args):
    path_var, _ = args.environment["PATH"]
    path_var.insert_at(0, "/Qux")
    args.environment.set_variable(path_var)

    args.VARIABLE = ["PATH"]
    args.SNAPSHOT = "test_save"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(list(filter(lambda x: x, stdout.split('\n'))) ==
           ["For variable 'PATH' the element '/Bar' will be removed.",
            "For variable 'PATH' the element '/Baz' will be added."])
    assert(not stderr)

    # The insertion happens at the front.
    assert(args.environment["PATH"][0].value == ["/Baz", "/Qux", "/Foo"])
    assert(args.environment.get_stamped_variable("PATH")[0].value ==
           ["/Baz", "/Foo"])

    assert(('+', "/Qux") in args.environment.diff()["PATH"].diff_actions)
