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
This Python module contains the declarations from which the **documentation**
for the schema of the data files used by the Variable Descriptions project.

This module is not loaded or compiled during normal execution of Envprobe.
"""
import os
import sys


if "sphinx" not in os.path.basename(sys.argv[0]):
    raise NotImplementedError("This module should not be loaded outside of "
                              "documentation generation!")


class Record:
    """
    """

    @property
    def Variable(self):
        """
        The name of the environment variable that the row is configuring.

        The value might be the literal ``__META__``, in which case the row
        identifies a :py:class:`MetaRecord`.

        Parameters
        ----------
        value : str

        .. versionadded:: 1.0
        """
        pass

    @property
    def TypeKind(self):
        """
        The :ref:`variable type<impl_vartypes_implemented_list>` of the
        variable.
        This is the textual identifier key of the `EnvVar` type class, as
        registered by :py:func:`envprobe.vartypes.load`.

        .. versionadded:: 1.0

        Parameters
        ----------
        value : str
        """
        pass

    @property
    def Description(self):
        """
        The textual comment that describes what the variable is used for.
        This value is shown by the :ref:`get --info command<envvars_get>` when
        the user requests.

        .. versionadded:: 1.0

        Parameters
        ----------
        value : str
        """
        pass


class MetaRecord:
    """
    If the :py:meth:`Record.Variable` field of the record equals the literal
    ``__META__``, a :py:class:`MetaRecord` is identified.
    Such records are parsed and handled differently than normal records of
    variables, but use the same format so they follow the CSV's general format.
    """

    @property
    def TypeKind(self):
        """
        A textual identifier key of which meta-variable the record specifies
        for the current data file.

        .. versionadded:: 1.0

        Parameters
        ----------
        value : choices
            See below for the potential kinds of meta-variables.
        """
        pass

    @property
    def Description(self):
        """
        The `Description` field contains the **value** for the meta-variable.
        The understanding of the individual values depends on the kind of the
        metavariable.

        .. versionadded:: 1.0
        """
        pass

    COMMENT = None
    """
    A textual comment or description of the contents of the data file.

    .. versionadded:: 1.0

    :meta hide-value:
    """
