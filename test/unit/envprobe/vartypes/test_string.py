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
from envprobe.vartypes.string import String


def test_init_and_load():
    s = String("test_string", "foo")
    assert(s.value == "foo")
    assert(s.raw() == "foo")


def test_setter():
    s = String("test_string", "foo")
    s.value = "bar"
    assert(s.value == "bar")
    assert(s.raw() == "bar")


def test_setter_nonstring():
    s = String("test_string", "foo")
    s.value = 42
    assert(type(s.value) == str)
    assert(s.value == "42")


def test_diff():
    s1 = String("test_string", "foo")
    s2 = String("test_string", "bar")

    diff = String.diff(s1, s2)
    assert(diff)
    assert(len(diff) == 2)
    assert(diff[0] == ('-', "foo"))
    assert(diff[1] == ('+', "bar"))


def test_no_diff():
    s = String("test_string", "foo")
    diff = String.diff(s, s)
    assert(not diff)


def test_diff_new():
    s1 = String("test_string", "")
    s2 = String("test_string", "bar")

    diff = String.diff(s1, s2)
    assert(len(diff) == 1)
    assert(diff[0] == ('+', "bar"))


def test_diff_remove():
    s1 = String("test_string", "")
    s2 = String("test_string", "bar")

    diff = String.diff(s2, s1)
    assert(len(diff) == 1)
    assert(diff[0] == ('-', "bar"))
