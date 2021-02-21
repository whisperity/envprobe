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

from envprobe import shell


def test_empty_environment():
    with pytest.raises(KeyError):
        shell.get_current_shell({})


def test_unknown_fails_to_load():
    with pytest.raises(ModuleNotFoundError):
        shell.get_current_shell({"ENVPROBE_SHELL_TYPE": "false"})


def test_non_subtype_mock_fails():
    class X:
        pass

    with pytest.raises(TypeError):
        shell.register_type("X", X)


def test_mock_registers_and_loads():
    with pytest.raises(KeyError):
        shell.get_class("fake")

    with pytest.raises(ModuleNotFoundError):
        shell.load("fake")

    shell.register_type("fake", shell.FakeShell)
    assert(shell.get_class("fake") == shell.FakeShell)

    # After registering, load() should not throw.
    assert(shell.load("fake") == shell.FakeShell)
