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


class MockVar:
    def __init__(self, name, raw_value):
        self.name = name
        self.value = raw_value

    @property
    def extended_attributes(self):
        return None

    def raw(self):
        return self.value


class MockEnv:
    def __init__(self):
        self.vars = {"TEST": MockVar("TEST", "Foo"),
                     "COMMUNITY": MockVar("COMMUNITY", "yes")
                     }

    def __getitem__(self, var_name):
        return self.vars.get(var_name, MockVar(var_name, "")), \
                var_name in self.vars


@pytest.fixture
def args():
    arg = Namespace()
    arg.environment = MockEnv()

    yield arg


def test_get_existing(capfd, args):
    args.VARIABLE = "TEST"
    args.info = False
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(stdout.rstrip() == "TEST=Foo")
    assert(not stderr)


def test_get_nonexistent(capfd, args):
    args.VARIABLE = "THIS DOESN'T EXIST"
    args.info = False
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(stderr.rstrip() == "THIS DOESN'T EXIST is not defined")


def test_info_builtin(capfd, args):
    args.VARIABLE = "TEST"
    args.info = True
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("Type: 'unknown'" in stdout)
    assert("test_get.MockVar" in stdout)
    assert("Description" not in stdout)
    assert("Source" not in stdout)
    assert(not stderr)
