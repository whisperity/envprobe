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

from envprobe.commands.remove import command
from envprobe.environment import Environment
from envprobe.shell import FakeShell


class FakeShell2(FakeShell):
    @property
    def manages_environment_variables(self):
        return True

    def _set_environment_variable(self, env_var):
        pass


class PathHeuristic:
    def __call__(self, name, env=None):
        return 'path'


@pytest.fixture
def cwd_to_root():
    wd = os.getcwd()
    os.chdir("/")
    yield None  # Allow running of the test code.
    os.chdir(wd)


@pytest.fixture
def args():
    shell = FakeShell2()
    envdict = {"PATH": "/Foo:/Bar:/Foo:/Foo:/Foo:/Bar"}

    arg = Namespace()
    arg.environment = Environment(shell, envdict, PathHeuristic())
    arg.shell = shell

    yield arg


def test_remove_path(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Bar"]
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] ==
           "/Foo:/Foo:/Foo:/Foo")


def test_remove_multiple(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Bar", "Foo"]
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] == "")


def test_remove_nonexistent(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["something"]
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] ==
           "/Foo:/Bar:/Foo:/Foo:/Foo:/Bar")
