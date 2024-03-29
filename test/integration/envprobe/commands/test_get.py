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

from envprobe.commands.get import command
from envprobe.environment import Environment
from envprobe.library import get_variable_information_manager
from envprobe.shell import FakeShell


class MockExtendedData:
    @property
    def type(self):
        return "string"

    @property
    def description(self):
        return "test"


class PathHeuristic:
    def __call__(self, name, env=None):
        return 'path'


@pytest.fixture
def args(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp_path, "cfg")

    shell = FakeShell()
    envdict = {"DUMMY_VAR": "VALUE",
               "PATH1": "/Foo:/Bar",
               "PATH_EMPTY": ""
               }

    arg = Namespace()
    arg.environment = Environment(shell, envdict, PathHeuristic())
    arg.shell = shell
    arg.info = True

    yield arg


def test_get_path_breakdown(capfd, args):
    args.VARIABLE = "PATH1"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("PATH1=/Foo:/Bar" in stdout)
    assert("PATH1:\n\t/Foo\n\t/Bar" in stdout)
    assert(not stderr)


def test_get_path_empty(capfd, args):
    args.VARIABLE = "PATH_EMPTY"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("PATH_EMPTY=" in stdout)
    assert("PATH_EMPTY:\n --- empty ---" in stdout)
    assert(not stderr)


def test_get_description_local(capfd, args):
    manager = get_variable_information_manager("DUMMY_VAR", read_only=False)
    manager.set("DUMMY_VAR", MockExtendedData(), "test-info")

    args.VARIABLE = "DUMMY_VAR"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("Type: 'path'" in stdout)
    assert("Description:\n\ttest" in stdout)
    assert("Source: test-info" in stdout)
    assert(not stderr)
