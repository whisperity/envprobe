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

from envprobe.vartypes.colon_separated import ColonSeparatedArray
from envprobe.vartypes.semi_separated import SemicolonSeparatedArray


def test_init_and_load():
    default = ColonSeparatedArray("default")
    assert(default.value == [])
    assert(default.raw() == "")

    a = ColonSeparatedArray("test_array", "Foo:Bar")
    assert(a.separator == ':')
    assert(a.value == ["Foo", "Bar"])
    assert(a.raw() == "Foo:Bar")
    assert(len(a) == 2)
    assert(a[0] == "Foo")
    assert(a[1] == "Bar")


def test_setter():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    a.value = "A:B"
    assert(a.separator == ':')
    assert(a.value == ["A", "B"])
    assert(a.raw() == "A:B")
    assert(len(a) == 2)
    assert(a[0] == "A")
    assert(a[1] == "B")


def test_setter_single():
    a = ColonSeparatedArray("test_array", "Foo")
    a.value = "42"
    assert(a.separator == ':')
    assert(a.value == ["42"])
    assert(a.raw() == "42")
    assert(len(a) == 1)
    assert(a[0] == "42")


def test_setter_other_sep():
    """
    Expect to see adding a value with ; "seperator" to be ignored and stay
    as its own element.
    """
    a = ColonSeparatedArray("test_array", "Foo")
    a.value = "A;B:Foo"
    assert(a.separator == ':')
    assert(a.value == ["A;B", "Foo"])
    assert(len(a) == 2)
    assert(a[0] == "A;B")


def test_setter_current_sep():
    """
    Expect rejecting adding a value that contains the current (:) separator.
    """
    a = ColonSeparatedArray("test_array", "Foo")

    with pytest.raises(ValueError):
        a.insert_at(-1, "Bar:Baz")

    with pytest.raises(ValueError):
        a[0] = "Foo:Bar"


def test_setitem():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    a[1] = "Baz"
    assert(a.value == ["Foo", "Baz"])

    with pytest.raises(IndexError):
        a[2] = "Qux"


def test_delitem():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    del a[0]
    assert(len(a) == 1)
    assert(a[0] == "Bar")

    del a[0]
    assert(len(a) == 0)
    assert(a.raw() == "")


def test_insert():
    a = ColonSeparatedArray("test_array", "Foo")

    # Insert at the end.
    a.insert_at(-1, "Bar")
    assert(len(a) == 2)
    assert(a[0] == "Foo")
    assert(a[1] == "Bar")

    # Insert at the beginning.
    a.insert_at(0, 42)
    assert(len(a) == 3)
    assert(a[0] == "42")
    assert(a[1] == "Foo")
    assert(a[2] == "Bar")

    # Insert as the second element.
    a.insert_at(1, "Baz")
    assert(len(a) == 4)
    assert(a[0] == "42")
    assert(a[1] == "Baz")
    assert(a[2] == "Foo")
    assert(a[3] == "Bar")

    # Insert as the second-to-last element.
    a.insert_at(-2, "Qux")
    assert(len(a) == 5)
    assert(a[0] == "42")
    assert(a[1] == "Baz")
    assert(a[2] == "Foo")
    assert(a[3] == "Qux")
    assert(a[4] == "Bar")

    assert(a.value == ["42", "Baz", "Foo", "Qux", "Bar"])


def test_insert_overflow():
    a = ColonSeparatedArray("test_array", ':'.join(map(str, range(1, 51))))
    assert(len(a) == 50)

    a.insert_at(-100, "X")
    a.insert_at(100, "Y")

    assert(a[0] == "X")
    assert(a[51] == "Y")

    assert(a.value == ["X"] + list(map(str, range(1, 51))) + ["Y"])


def test_remove_element():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    a.remove_value("Foo")
    assert(len(a) == 1)
    assert(a[0] == "Bar")

    a = ColonSeparatedArray("test_array", "Foo:Bar:Foo")
    a.remove_value("Foo")
    assert(len(a) == 1)
    assert(a[0] == "Bar")


def test_diff():
    a1 = ColonSeparatedArray("test_array", "Foo:Bar")
    a2 = ColonSeparatedArray("test_array", "Foo:Bar:Baz")

    diff = ColonSeparatedArray.diff(a1, a2)
    assert(len(diff) == 3)
    assert(diff[0] == ('=', "Foo"))
    assert(diff[1] == ('=', "Bar"))
    assert(diff[2] == ('+', "Baz"))

    a3 = ColonSeparatedArray("test_array_empty", "")
    diff = ColonSeparatedArray.diff(a2, a3)
    assert(len(diff) == 3)
    assert(diff[0] == ('-', "Foo"))
    assert(diff[1] == ('-', "Bar"))
    assert(diff[2] == ('-', "Baz"))


def test_no_diff():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    diff = ColonSeparatedArray.diff(a, a)
    assert(not diff)


def test_semicolon():
    a = SemicolonSeparatedArray("test_array_semi", "Foo:Bar;Baz")
    assert(len(a) == 2)
    assert(a.value == ["Foo:Bar", "Baz"])


def test_apply_diff():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    a.apply_diff([('=', "Foo"), ('-', "Bar"), ('+', "Baz")])
    assert(a.value == ["Foo", "Baz"])

    a.apply_diff([("+", "Qux")])
    assert(a.value == ["Foo", "Baz", "Qux"])

    a.apply_diff([])
    assert(a.value == ["Foo", "Baz", "Qux"])

    a.apply_diff([('-', "NonexistentValue")])
    assert(a.value == ["Foo", "Baz", "Qux"])


def test_merge_diff():
    diff_1 = [('=', "Foo"), ('+', "Bar")]
    assert(ColonSeparatedArray.merge_diff(diff_1, []) == [('+', "Bar")])
    assert(ColonSeparatedArray.merge_diff([], diff_1) == [('+', "Bar")])

    diff_2 = [('-', "Foo"), ('+', "Bar")]
    assert(ColonSeparatedArray.merge_diff(diff_1, diff_2) ==
           [('-', "Foo"), ('+', "Bar")])

    diff_3 = [('=', "Foo"), ('-', "Bar")]
    assert(ColonSeparatedArray.merge_diff(diff_1, diff_3) == [])
    assert(ColonSeparatedArray.merge_diff(
        ColonSeparatedArray.merge_diff(diff_1, diff_2), diff_3) ==
           [('-', 'Foo')])

    diff_4 = ["Foo"]
    assert(ColonSeparatedArray.merge_diff(diff_4, diff_1) ==
           [('+', "Foo"), ('+', "Bar")])
