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
from envprobe.settings.snapshot import Snapshot


def test_setup():
    s = Snapshot()
    assert(s["FOO"] is None)


def test_set_and_get():
    s = Snapshot()
    s["FOO"] = {"diff object"}

    assert(s["FOO"] == {"diff object"})
    assert(s["BAR"] is None)


def test_delete():
    s = Snapshot()
    s["FOO"] = 1
    del s["FOO"]

    assert(s["FOO"] is s.UNDEFINE)
    assert(s["BAR"] is None)
