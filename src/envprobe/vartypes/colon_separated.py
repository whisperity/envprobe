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
from envprobe.vartypes.array import Array
from envprobe.vartypes.envvar import register_type


class ColonSeparatedArray(Array):
    """A helper class that binds the array's :py:attr:`separator` to ``:``."""

    def __init__(self, name, raw_value=""):
        """"""
        super().__init__(name, ':', raw_value)

    @classmethod
    def type_description(cls):
        """A list of strings in an array, separated by :"""
        return "A list of strings in an array, separated by :"


register_type('colon_separated', ColonSeparatedArray)
