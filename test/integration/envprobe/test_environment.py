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
import os
import pytest
import random
import string

from envprobe.environment import Environment, EnvVarTypeHeuristic
from envprobe.environment import VariableDifferenceKind as VDK
from envprobe.shell import Shell, get_current_shell
from envprobe.shell import register_type as register_shell
from envprobe.vartypes import EnvVar
from envprobe.vartypes import register_type as register_envvar


def _register_mock_shell(rand):
    class MockShell(Shell):
        def __init__(self, pid, config_dir):
            super().__init__(pid, config_dir, "control.txt")

        @property
        def is_envprobe_capable(self):
            return True

        def get_shell_hook(self, envprobe_callback_location):
            pass

        def get_shell_unhook(self):
            pass

        @property
        def manages_environment_variables(self):
            return True

        def _set_environment_variable(self, env_var):
            pass

        def _unset_environment_variable(self, env_var):
            pass

    register_shell(rand, MockShell)


@pytest.fixture
def mock_shell(scope="module"):
    """Generate a randomly named `MockShell` and register it."""
    rand_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    _register_mock_shell(rand_str)
    yield rand_str


@pytest.fixture
def dummy_shell(mock_shell, tmp_path):
    cfg = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
           "ENVPROBE_CONFIG": str(tmp_path),
           "ENVPROBE_SHELL_TYPE": mock_shell}

    env = {"USER": "envprobe",
           "CURRENT_DAY": random.randint(1, 31),
           "INIT_PID": 1,
           "PATH": "/bin:/usr/bin",
           "CMAKE_LIST": "MyModule;FooBar",
           **cfg}

    return get_current_shell(env), env


def _register_mock_variable(rand):
    class MockVariable(EnvVar):
        def __init__(self, variable, value=""):
            super().__init__(variable, value)
            self.value = value

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, new_value):
            self._value = new_value

        def raw(self):
            return self._value

    register_envvar(rand, MockVariable)

    class MockVarHeuristic(EnvVarTypeHeuristic):
        def __call__(self, name, env=None):
            return rand

    return MockVariable, MockVarHeuristic()


@pytest.fixture
def mock_envvar(scope="module"):
    """Generate a randomly named `MockVariable` and the appropriate heuristics,
    and register it.
    """
    rand_str = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    MockVar, MockHeuristics = _register_mock_variable(rand_str)
    yield MockVar, MockHeuristics


@pytest.fixture
def dummy_env(dummy_shell, mock_envvar):
    shell, osenv = dummy_shell
    _, MockHeuristics = mock_envvar
    environment = Environment(shell, osenv, MockHeuristics)
    return environment


def test_load_default_state(dummy_shell, dummy_env):
    _, osenv = dummy_shell
    assert(dummy_env.current_environment == osenv)
    assert(not dummy_env.stamped_environment)


def test___getitem__(dummy_env):
    existing_var, existing = dummy_env["USER"]
    assert(existing_var.name == "USER")
    assert(existing_var.value == "envprobe")
    assert(existing)

    not_existing_var, not_existing = dummy_env["TEST"]
    assert(not_existing_var.name == "TEST")
    assert(not_existing_var.value == "")
    assert(not not_existing)


def test_get_stamped_variable(dummy_env):
    dummy_env.stamp()

    existing_var, existing = dummy_env.get_stamped_variable("USER")
    assert(existing_var.name == "USER")
    assert(existing_var.value == "envprobe")
    assert(existing)

    not_existing_var, not_existing = dummy_env.get_stamped_variable("TEST")
    assert(not_existing_var.name == "TEST")
    assert(not_existing_var.value == "")
    assert(not not_existing)


def test_save_stamp(dummy_shell, dummy_env):
    shell, osenv = dummy_shell
    dummy_env.stamp()
    assert(dummy_env.current_environment == osenv)
    assert(dummy_env.stamped_environment == osenv)

    dummy_env.save()
    assert(os.path.isfile(shell.state_file))


def test_change(dummy_shell, mock_envvar, dummy_env):
    shell, osenv = dummy_shell
    _, MockHeuristics = mock_envvar

    dummy_env.stamp()
    dummy_env.save()

    with open(shell.state_file, 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(0, 0)
        state_data = f.read(size)

    # Save file is produced. Now we change the environment and load a new one
    # for the *same* shell, simulating Envprobe accessing the same shell's
    # env after a change.
    osenv["USER"] = "root"
    del osenv["INIT_PID"]
    osenv["TEST"] = "test"

    dummy_env = Environment(shell, osenv, MockHeuristics)
    assert(dummy_env.current_environment != dummy_env.stamped_environment)

    diff = dummy_env.diff()
    add = diff["TEST"]
    assert(add.variable == "TEST" and add.kind == VDK.ADDED)

    rm = diff["INIT_PID"]
    assert(rm.variable == "INIT_PID" and rm.kind == VDK.REMOVED)

    mod = diff["USER"]
    assert(mod.variable == "USER" and mod.kind == VDK.CHANGED)

    dummy_env.stamp()
    assert(not dummy_env.diff())

    dummy_env.save()
    with open(shell.state_file, 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(0, 0)
        state_data_new = f.read(size)

    assert(state_data != state_data_new)


def test_apply_change(dummy_shell, mock_envvar, dummy_env):
    shell, osenv = dummy_shell
    MockVar, MockHeuristics = mock_envvar

    dummy_env.save()
    dummy_env.stamp()
    assert(dummy_env.current_environment == dummy_env.stamped_environment)

    user = MockVar("USER", "root")
    dummy_env.apply_change(user)
    assert(dummy_env.current_environment != dummy_env.stamped_environment)
    diff = dummy_env.diff()
    # The diff is: USER is "root" in stamped, and "envprobe" in current.
    assert(len(diff) == 1 and "USER" in diff)
    assert(diff["USER"].kind == VDK.CHANGED)

    dummy_env.save()  # stamped -> disk.
    # disk -> current.
    dummy_env = Environment(shell, {**osenv, "USER": "root"}, MockHeuristics)
    assert(dummy_env.current_environment == dummy_env.stamped_environment)

    init_pid = MockVar("INIT_PID", None)
    dummy_env.apply_change(init_pid, remove=True)
    assert(dummy_env.current_environment != dummy_env.stamped_environment)
    diff = dummy_env.diff()
    # The diff is: INIT_PID is NOT part of stamped, but part of current.
    assert(len(diff) == 1 and "INIT_PID" in diff)
    assert(diff["INIT_PID"].kind == VDK.ADDED)


def test_diff(dummy_shell, mock_envvar, dummy_env):
    shell, osenv = dummy_shell
    MockVar, MockHeuristics = mock_envvar
    dummy_env.stamp()
    assert(not dummy_env.diff())

    var = MockVar("X", 8)
    dummy_env.set_variable(var)

    user_var, _ = dummy_env["USER"]
    assert(type(user_var) is MockVar)
    dummy_env.set_variable(user_var, remove=True)

    init_pid_var, _ = dummy_env["INIT_PID"]
    init_pid_var.value = 42
    dummy_env.set_variable(init_pid_var)

    diff = dummy_env.diff()
    assert(len(diff) == 3)

    assert(diff["USER"].diff_actions == [('-', "envprobe")])
    assert(diff["X"].diff_actions == [('+', 8)])
    assert(diff["INIT_PID"].diff_actions == [('-', 1), ('+', 42)])
