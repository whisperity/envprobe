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

from envprobe.community_descriptions.local_data import MetaConfiguration


def test_setup():
    i = MetaConfiguration()
    assert(i.version == '0' * 41)


def test_set_and_get():
    i = MetaConfiguration()
    i.set_comment_for("foo", "bar")
    assert(i.get_comment_for("foo") == "bar")


def test_delete():
    i = MetaConfiguration()
    i.set_comment_for("foo", "bar")
    i.set_comment_for("baz", "qux")

    i.delete_source("foo")

    assert(i.get_comment_for("baz") == "qux")

    with pytest.raises(KeyError):
        i.get_comment_for("foo")
