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
from envprobe.environment import VariableDifference
from envprobe.environment import VariableDifferenceKind as VDK


def test_diff_new():
    diff = VariableDifference(VDK.ADDED, "X", None, "Bar",
                              [('+', "Bar")])
    assert(diff.is_simple_change)
    assert(diff.is_new)
    assert(not diff.is_unset)


def test_diff_del():
    diff = VariableDifference(VDK.REMOVED, "X", "Foo", None,
                              [('-', "Foo")])
    assert(diff.is_simple_change)
    assert(not diff.is_new)
    assert(diff.is_unset)


def test_diff_simple():
    diff = VariableDifference(VDK.CHANGED, "X", "Foo", "Bar",
                              [('-', "Foo"), ('+', "Bar")])
    assert(diff.is_simple_change)
    assert(not diff.is_new)
    assert(not diff.is_unset)


def test_diff_not_simple():
    diff = VariableDifference(VDK.CHANGED, "PATH", "/x:/y", "/x:/z",
                              [('=', "/x"),
                               ('+', "/z"),
                               ('-', "/y")
                               ])
    assert(not diff.is_simple_change)
    assert(not diff.is_new)
    assert(not diff.is_unset)
