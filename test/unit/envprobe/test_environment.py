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
import pytest

from envprobe.environment import Environment
from envprobe.shell import Shell


class MockVar:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def raw(self):
        return self.value


class MockShell(Shell):
    def __init__(self):
        pass

    @property
    def is_envprobe_capable(self):
        return False

    def get_shell_hook(self):
        pass

    def get_shell_unhook(self):
        pass

    @property
    def manages_environment_variables(self):
        return False


@pytest.fixture
def env():
    envp = {"TEST": "Foo"}
    return Environment(MockShell(), envp)


def test_set_variable(env):
    assert(env.current_environment["TEST"] == "Foo")
    assert(not env.stamped_environment)

    var = MockVar("TEST", "Bar")
    env.set_variable(var)

    assert(env.current_environment["TEST"] == "Bar")

    env.stamp()

    assert(env.current_environment["TEST"] == env.stamped_environment["TEST"])

    var.value = "Qux"
    env.set_variable(var, remove=True)

    assert("TEST" not in env.current_environment)
    assert(env.stamped_environment["TEST"] == "Bar")


def test_apply_change(env):
    assert(env.current_environment["TEST"] == "Foo")
    assert(not env.stamped_environment)

    var = MockVar("TEST", "Bar")
    env.apply_change(var)

    assert(env.stamped_environment["TEST"] == "Bar")
    assert(env.current_environment["TEST"] != env.stamped_environment["TEST"])

    var.value = "Qux"
    env.apply_change(var, remove=True)

    assert(env.current_environment["TEST"] == "Foo")
    assert("TEST" not in env.stamped_environment)
