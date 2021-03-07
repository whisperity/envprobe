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
import pytest

from envprobe.commands.diff import command, Format
from envprobe.environment import Environment
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
def args():
    shell = FakeShell2()
    envdict = {"PATH": "/Foo:/Bar",
               "FOO": "Foo",
               "NUM": "8"}

    arg = Namespace()
    arg.environment = Environment(shell, envdict, PathHeuristic())
    arg.shell = shell
    arg.tracking = MockTracking()

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

    yield arg


def test_diff_human(capfd, args):
    args.VARIABLE = None
    args.output_type = Format.HUMAN_READABLE
    command(args)

    stdout, stderr = capfd.readouterr()
    expected = ["(!) Changed:     FOO",
                "\tchanged from:  Foo",
                "\tchanged to:    Bar",
                "(-) Removed:     NUM",
                "\tvalue was:     8",
                "(!) Changed:     PATH",
                "\tremoved:       /Bar",
                "\tadded:         /Baz"
                ]
    assert(stdout)
    assert(list(filter(lambda x: x, stdout.split('\n'))) == expected)
    assert(not stderr)


def test_diff_human_specific_variable(capfd, args):
    args.VARIABLE = ["FOO"]
    args.output_type = Format.HUMAN_READABLE
    command(args)

    stdout, stderr = capfd.readouterr()
    expected = ["(!) Changed:     FOO",
                "\tchanged from:  Foo",
                "\tchanged to:    Bar"
                ]
    assert(stdout)
    assert(list(filter(lambda x: x, stdout.split('\n'))) == expected)
    assert(not stderr)


def test_diff_human_respect_tracking(capfd, args):
    args.VARIABLE = None
    args.output_type = Format.HUMAN_READABLE
    args.tracking._ignore("PATH")
    command(args)

    stdout, stderr = capfd.readouterr()
    expected = ["(!) Changed:     FOO",
                "\tchanged from:  Foo",
                "\tchanged to:    Bar",
                "(-) Removed:     NUM",
                "\tvalue was:     8"
                ]
    assert(stdout)
    assert(list(filter(lambda x: x, stdout.split('\n'))) == expected)
    assert(not stderr)


def test_diff_unified(capfd, args):
    args.VARIABLE = None
    args.output_type = Format.UNIFIED
    command(args)

    stdout, stderr = capfd.readouterr()
    expected = ["--- FOO",
                "+++ FOO",
                "@@ -1,1 +1,1 @@",
                "-Foo",
                "+Bar",
                "--- NUM",
                "+++ /dev/null",
                "@@ -1,1 +0,0 @@",
                "-8",
                "--- PATH",
                "+++ PATH",
                "@@ -1,2 +1,2 @@",
                " /Foo",
                "-/Bar",
                "+/Baz"
                ]
    assert(stdout)
    assert(list(filter(lambda x: x, stdout.split('\n'))) == expected)
    assert(not stderr)
