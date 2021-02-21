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

from envprobe.shell.bash import Bash


class MockVar:
    def __init__(self, var_name, value):
        self.name = var_name
        self.value = value

    def raw(self):
        return self.value


@pytest.fixture
def sh(tmp_path):
    return Bash(random.randint(1024, 65536), str(tmp_path))


def _control_lines(shell):
    with open(shell.control_file, 'r') as cfile:
        return list(map(lambda x: x.strip(),
                        filter(lambda x: x != '\n', cfile)))


def test_load(sh):
    assert(os.path.basename(sh.control_file) == "control.sh")
    assert(sh.is_envprobe_capable)
    assert(sh.manages_environment_variables)
    assert("PROMPT_COMMAND" in sh.get_shell_hook(""))


def test_set(sh):
    s = MockVar("test", "foo")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export test=foo;" in lines)


def test_set_two(sh):
    s1 = MockVar("test", "foo")
    s2 = MockVar("test2", "bar")
    sh.set_environment_variable(s1)
    sh.set_environment_variable(s2)

    lines = _control_lines(sh)
    assert(len(lines) == 2)
    assert("export test=foo;" in lines)
    assert("export test2=bar;" in lines)


def test_set_pathy(sh):
    s = MockVar("test_path", "Foo:Bar")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export test_path=Foo:Bar;" in lines)


def test_set_spacey(sh):
    s = MockVar("has_spaces", "a b")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export has_spaces='a b';" in lines)


def test_unset(sh):
    s1 = MockVar("test", "foo")
    sh.unset_environment_variable(s1)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("unset test;" in lines)


def test_set_and_unset(sh):
    s1 = MockVar("test", "foo")
    s2 = MockVar("test2", "bar")
    sh.set_environment_variable(s1)
    sh.unset_environment_variable(s2)

    lines = _control_lines(sh)
    assert(len(lines) == 2)
    assert("export test=foo;" in lines)
    assert("unset test2;" in lines)
