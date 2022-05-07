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
from envprobe.vartypes.envvar import EnvVar, register_type


class Numeric(EnvVar):
    """This type may only hold a numeric (:py:class:`int` or
    :py:class:`float`) value.
    """

    def __init__(self, name, raw_value="0"):
        """Create a new :py:class:`Numeric` variable by converting
        `raw_value`."""
        super().__init__(name, raw_value)
        self.value = raw_value

    @classmethod
    def type_description(cls):
        """Contains a value that must be an integer or floating-point number.
        """
        return "Contains a value that must be an integer or floating-point " \
               "number."

    @property
    def value(self):
        """Get the value of the variable.

        Returns
        -------
        int or float
            The value.
        """
        return self._value

    @value.setter
    def value(self, new_value):
        """Sets the :py:attr:`value` to `new_value`.

        Parameters
        ----------
        new_value: int or float
            The new value.

        Raises
        ------
        ValueError
            If the given value is neither :py:class`int` nor :py:class`float`.
        """
        # First, try to make the variable a float. Every int can be a float
        # implicitly.
        try:
            self._value = float(new_value)
            self._kind = float
        except ValueError:
            raise

        if self._value.is_integer():
            # If the float is actually an integer, cast to integer.
            self._value = int(self._value)
            self._kind = int

    @property
    def is_integer(self):
        """Whether the value is of :py:class:`int` type."""
        return self._kind == int

    @property
    def is_floating(self):
        """Whether the value is of :py:class:`float` type."""
        return self._kind == float

    def raw(self):
        """Convert the value to raw shell representation, i.e.
        a :py:class:`str`.
        """
        return str(self.value)

    @classmethod
    def _diff(cls, old, new):
        """Generate a difference between `old` and `new` values.

        Unlike :py:func:`EnvVar.diff`, the difference of `Numeric` variables
        will always have a ``-`` ("removed") and a ``+`` ("added") side.
        """
        return [('-', old.raw()), ('+', new.raw())] \
            if old.value != new.value else []


register_type('numeric', Numeric)
