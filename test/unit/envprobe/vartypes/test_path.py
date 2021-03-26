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
"""
Tests the "Path" environment variable implementation.

This is largely the same as testing generic separated arrays, except that
values expand to absolute paths.
"""
import os
import pytest

from envprobe.vartypes.path import Path


@pytest.fixture
def cwd_to_root():
    wd = os.getcwd()
    os.chdir("/")
    yield None  # Allow running of the test code.
    os.chdir(wd)


def test_init_and_load(cwd_to_root):
    a = Path("test_path", "Foo:Bar")
    assert(a.separator == ':')
    assert(a.value == ["/Foo", "/Bar"])
    assert(a.raw() == "/Foo:/Bar")
    assert(len(a) == 2)
    assert(a[0] == "/Foo")
    assert(a[1] == "/Bar")


def test_abspath(cwd_to_root):
    a = Path("test_path", "~/Foobar/Install/../Build/lib/lib32/..")
    assert(a.value == ["/~/Foobar/Build/lib"])


def test_setter(cwd_to_root):
    a = Path("test_array", "Foo:Bar")
    a.value = "A:B"
    assert(a.separator == ':')
    assert(a.value == ["/A", "/B"])
    assert(a.raw() == "/A:/B")
    assert(len(a) == 2)
    assert(a[0] == "/A")
    assert(a[1] == "/B")


def test_setter_single(cwd_to_root):
    a = Path("test_array", "Foo")
    a.value = "42"
    assert(a.separator == ':')
    assert(a.value == ["/42"])
    assert(a.raw() == "/42")
    assert(len(a) == 1)
    assert(a[0] == "/42")


def test_setter_other_sep(cwd_to_root):
    """
    Expect to see adding a value with ; "seperator" to be ignored and stay
    as its own element.
    """
    a = Path("test_array", "Foo")
    a.value = "A;B:Foo"
    assert(a.separator == ':')
    assert(a.value == ["/A;B", "/Foo"])
    assert(len(a) == 2)
    assert(a[0] == "/A;B")


def test_setter_current_sep(cwd_to_root):
    """
    Expect rejecting adding a value that contains the current (:) separator.
    """
    a = Path("test_array", "Foo")

    with pytest.raises(ValueError):
        a.insert_at(-1, "Bar:Baz")

    with pytest.raises(ValueError):
        a[0] = "Foo:Bar"


def test_setitem(cwd_to_root):
    a = Path("test_array", "Foo:Bar")
    a[1] = "Baz"
    assert(a.value == ["/Foo", "/Baz"])

    with pytest.raises(IndexError):
        a[2] = "Qux"


def test_delitem(cwd_to_root):
    a = Path("test_array", "Foo:Bar")
    del a[0]
    assert(len(a) == 1)
    assert(a[0] == "/Bar")

    del a[0]
    assert(len(a) == 0)
    assert(a.raw() == "")


def test_remove_element(cwd_to_root):
    a = Path("test_array", "Foo:Bar")
    a.remove_value("Foo")
    assert(len(a) == 1)
    assert(a[0] == "/Bar")

    a = Path("test_array", "Foo:Bar:Foo")
    a.remove_value("Foo")
    assert(len(a) == 1)
    assert(a[0] == "/Bar")


def test_diff(cwd_to_root):
    a1 = Path("test_array", "Foo:Bar")
    a2 = Path("test_array", "Foo:Bar:Baz")

    diff = Path.diff(a1, a2)
    assert(len(diff) == 3)
    assert(diff[0] == ('=', "/Foo"))
    assert(diff[1] == ('=', "/Bar"))
    assert(diff[2] == ('+', "/Baz"))

    a3 = Path("test_array_empty", "")
    diff = Path.diff(a2, a3)
    assert(len(diff) == 3)
    assert(diff[0] == ('-', "/Foo"))
    assert(diff[1] == ('-', "/Bar"))
    assert(diff[2] == ('-', "/Baz"))


def test_no_diff(cwd_to_root):
    a = Path("test_array", "Foo:Bar")
    diff = Path.diff(a, a)
    assert(not diff)


def test_apply_diff(cwd_to_root):
    a = Path("test_array", "Foo:Bar")
    a.apply_diff([('=', "Foo"), ('-', "Bar"), ('+', "Baz")])
    assert(a.value == ["/Baz", "/Foo"])

    a.apply_diff([('-', "Baz"), ('+', "/xxx/Baz")])
    assert(a.value == ["/xxx/Baz", "/Foo"])

    a.apply_diff([("+", "Qux")])
    assert(a.value == ["/Qux", "/xxx/Baz", "/Foo"])

    a.apply_diff([])
    assert(a.value == ["/Qux", "/xxx/Baz", "/Foo"])

    a.apply_diff([('-', "NonexistentValue")])
    assert(a.value == ["/Qux", "/xxx/Baz", "/Foo"])
