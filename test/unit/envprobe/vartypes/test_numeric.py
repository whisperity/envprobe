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

from envprobe.vartypes.numeric import Numeric


def test_init_and_load():
    default = Numeric("default")
    assert(default.value == 0)
    assert(default.raw() == "0")

    n = Numeric("test_int", 42)
    assert(n.is_integer)
    assert(not n.is_floating)
    assert(n.value == 42)
    assert(n.raw() == "42")

    n2 = Numeric("test_float", 1.5)
    assert(not n2.is_integer)
    assert(n2.is_floating)
    assert(n2.value == 1.5)
    assert(n2.raw() == "1.5")

    n3 = Numeric("test_int_from_str", "10")
    assert(n3.is_integer)
    assert(not n3.is_floating)
    assert(n3.value == 10)
    assert(n3.raw() == "10")


def test_setter():
    n = Numeric("test_int", 42)
    n.value = 0
    assert(n.is_integer)
    assert(n.value == 0)
    assert(n.raw() == "0")


def test_setter_nonint():
    n = Numeric("test_int", 42)
    with pytest.raises(ValueError):
        n.value = "foo"


def test_diff():
    n1 = Numeric("test_int", 1)
    n2 = Numeric("test_int", 2)

    diff = Numeric.diff(n1, n2)
    assert(len(diff) == 2)
    assert(diff[0] == ('-', "1"))
    assert(diff[1] == ('+', "2"))


def test_no_diff():
    n = Numeric("test_int", 1)
    diff = Numeric.diff(n, n)
    assert(not diff)


def test_apply_diff():
    n1 = Numeric("test_number", 0)
    n1.apply_diff([('-', 2), ('+', 4)])
    assert(n1.value == 4)

    with pytest.raises(ValueError) as exc_info:
        n1.apply_diff([])
    assert("Bad diff" in str(exc_info.value))

    with pytest.raises(ValueError) as exc_info:
        n1.apply_diff([('+', 5), ('+', 10)])
    assert("Bad diff" in str(exc_info.value))

    with pytest.raises(ValueError) as exc_info:
        n1.apply_diff([('+', "foo")])
    assert("could not convert" in str(exc_info.value))


def test_merge_diff():
    assert(Numeric.merge_diff([], []) == [])

    assert(Numeric.merge_diff([('-', 1)], []) == [])

    assert(Numeric.merge_diff([], [('-', 1)]) == [])

    assert(Numeric.merge_diff([('+', 1)], []) == [('+', 1)])

    assert(Numeric.merge_diff([('+', 1)], [('+', 2)]) == [('+', 2)])

    assert(Numeric.merge_diff([('-', 1), ('+', 2)],
                              [('-', 3), ('+', 4)]) == [('+', 4)])

    with pytest.raises(ValueError) as exc_info:
        Numeric.merge_diff([('+', 1), ('+', 2)], [])
    assert("Bad diff" in str(exc_info.value))
