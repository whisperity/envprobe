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

from envprobe.commands.undefine import command


class MockVar:
    def __init__(self, name, raw_value):
        self.name = name
        self.value = raw_value

    def raw(self):
        return self.value


class MockShell:
    def __init__(self):
        self.m_vars = ["TEST"]

    def unset_environment_variable(self, env_var):
        self.m_vars.remove(env_var.name)


class MockEnv:
    def __init__(self):
        self.vars = {"TEST": MockVar("TEST", "Foo")}

    def __getitem__(self, var_name):
        return self.vars.get(var_name, MockVar(var_name, "")), \
                var_name in self.vars

    def set_variable(self, env_var, remove=False):
        if remove:
            del self.vars[env_var.name]
        else:
            raise NotImplementedError("Not-removing is not supported!")


@pytest.fixture
def args():
    arg = Namespace()
    arg.shell = MockShell()
    arg.environment = MockEnv()

    yield arg


def test_undefine_existing(capfd, args):
    args.VARIABLE = "TEST"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert("TEST" not in args.shell.m_vars)
    assert("TEST" not in args.environment.vars)


def test_undefine_nonexistent(capfd, args):
    args.VARIABLE = "THIS DOESN'T EXIST"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert("THIS DOESN'T EXIST" not in args.shell.m_vars)
    assert("THIS DOESN'T EXIST" not in args.environment.vars)
