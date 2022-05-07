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
Implementation of PATH-like arrays.
"""
import os

from envprobe.vartypes.envvar import register_type
from envprobe.vartypes.colon_separated import ColonSeparatedArray


class Path(ColonSeparatedArray):
    """A POSIX-compatible ``PATH`` environment variable.

    ``PATH`` variables are commonly used as list of locations (directories,
    and, rarely, files) on the filesystem in an order of precedence for finding
    various system elements. ``PATH`` variables in POSIX are separated by
    ``:``, except in rare circumstances.

    This class extends
    :py:class:`envprobe.vartypes.colon_separated.ColonSeparatedArray` with
    automatically converting the given paths (when the array is constructed or
    modified) to **absolute paths**, by calling :py:func:`os.path.abspath` on
    the value.

    Symbolic links are kept and variable sequences such as ``~`` remain
    unexpanded, however, relative references (``a/../b`` to ``b``) are removed
    and the current working directory (:py:func:`os.getcwd`) is prepended.
    """
    def __init__(self, name, raw_value=""):
        """Create a :py:class:`Path` from the given `raw_value`."""
        super().__init__(name, raw_value)

    def _transform_element_set(self, elem):
        """Transforms the `elem` to an absolute path."""
        elem = super()._transform_element_set(elem)
        if elem:
            elem = os.path.abspath(elem)
        return elem

    @classmethod
    def type_description(cls):
        """A list of directories (and sometimes files) separated by :, and
        automatically expanded to absolute paths."""
        return "A list of directories (and sometimes files) separated by :, " \
               "and automatically expanded to absolute paths."""

    def apply_diff(self, diff):
        """Applies the given `diff` actions.

        For :py:class:`Path` variables, the diff application is element-wise.
        Elements that do not exist but are meant to be removed are ignored.
        New elements are added at the **front** of the array.
        """
        if not diff:
            return

        for mode, value in diff:
            if mode == '-':
                self.remove_value(value)
            elif mode == '=':
                continue
            elif mode == '+':
                self.insert_at(0, value)


register_type('path', Path)
