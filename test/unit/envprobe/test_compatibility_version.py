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

from envprobe.compatibility import Version


def test_parser():
    assert(Version(None).components == (0, 0))
    assert(Version("1").components == (1, 0))
    assert(Version("1.2").components == (1, 2))
    assert(Version("9.8.9").components == (9, 8))


def test_str():
    assert(str(Version(None)) == "0.0")
    assert(str(Version("1")) == "1.0")
    assert(str(Version("1.2")) == "1.2")
    assert(str(Version("9.8.9")) == "9.8")


def test_equal():
    assert(Version(None) == Version(None))
    assert(Version(None) != Version("1.0"))
    assert(Version("2.0") == Version("2.0"))
    assert(Version("2.0") != Version("2.1"))
    assert(not Version(None) != Version(None))


def test_compare():
    assert(Version("1.0") <= Version("1.0"))
    assert(Version("1.0") <= Version("1.1"))
    assert(Version("1.0") < Version("1.1"))
    assert(Version("1.0") >= Version("1.0"))
    assert(Version("1.1") >= Version("1.0"))
    assert(Version("1.1") > Version("1.0"))

    assert(not Version("1.0") > Version("2.0"))
    assert(not Version("2.0") < Version("1.0"))
