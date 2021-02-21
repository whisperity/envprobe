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

from envprobe import vartypes


def test_empty():
    with pytest.raises(KeyError):
        vartypes.get_class("invalid")


def test_invalid_type_fails_to_load():
    with pytest.raises(ModuleNotFoundError):
        vartypes.load("false-type")


def test_non_subtype_mock_fails():
    class X:
        pass

    with pytest.raises(TypeError):
        vartypes.register_type("X", X)


class MockVariable(vartypes.EnvVar):
    pass


def test_mock_registers_and_loads():
    with pytest.raises(KeyError):
        vartypes.get_class("fake")

    with pytest.raises(ModuleNotFoundError):
        vartypes.load("fake")

    vartypes.register_type("fake", MockVariable)
    assert(vartypes.get_class("fake") == MockVariable)

    # After registering, load() should not throw either.
    assert(vartypes.load("fake") == MockVariable)
