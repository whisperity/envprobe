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

from envprobe.commands.get import command
from envprobe.environment import Environment
from envprobe.shell import FakeShell


class MockCommunity:
    def get_description(self, var_name):
        return dict()


class PathHeuristic:
    def __call__(self, name, env=None):
        return 'path'


@pytest.fixture
def args():
    shell = FakeShell()
    envdict = {"PATH1": "/Foo:/Bar",
               "PATH_EMPTY": ""
               }

    arg = Namespace()
    arg.community = MockCommunity()
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
