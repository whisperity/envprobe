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


class Version:
    """A basic class of program versions epxressed in the two-part `M.m`
    (major, minor) format.

    Note
    ----
        This class is implemented so that Envprobe does not need to depend on
        the **setuptools** package.
    """
    def __init__(self, val):
        """Initialises a version by parsing the string representation."""
        if val is None:
            val = "0.0"

        parts = val.split('.')
        self.major = int(parts[0]) if len(parts) >= 1 else 0
        self.minor = int(parts[1]) if len(parts) >= 2 else 0

    @property
    def components(self):
        """Returns the tuple of the version's components."""
        return (self.major, self.minor)

    def __str__(self):
        return "{}.{}".format(*self.components)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.major < other.major or \
            (self.major == other.major and self.minor < other.minor)

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return self.major > other.major or \
            (self.major == other.major and self.minor > other.minor)

    def __le__(self, other):
        return not self > other
