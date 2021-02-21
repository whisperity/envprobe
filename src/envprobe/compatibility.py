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
"""Implement some certain compatibility features between Python versions."""

try:
    # nullcontext() is only available starting Python 3.7.
    from contextlib import nullcontext
except ImportError:
    class _ContextWrapper:
        def __init__(self, obj):
            self._obj = obj

        def __enter__(self):
            return self._obj

        def __exit__(self, *args):
            pass

    def nullcontext(enter_result=None):
        """Returns a context manager that returns `enter_result` from
        ``__enter__``, but otherwise does nothing.
        """
        return _ContextWrapper(enter_result)
