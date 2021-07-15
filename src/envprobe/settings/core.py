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
import os
import tempfile


def get_configuration_directory():
    """Returns the location where Envprobe's user-specific configuration files
    are stored.

    This method uses ``$XDG_CONFIG_HOME`` as per FreeDesktop specifications, if
    exists.
    Otherwise, the ``.config`` directory under the user's `HOME` will be used.
    """
    basedir = os.environ.get("XDG_CONFIG_HOME",
                             os.path.join(os.path.expanduser('~'),
                                          ".config"))
    return os.path.join(basedir, "envprobe")


def get_data_directory():
    """Returns the location where Envprobe's user-specific changing data is.

    This method uses ``$XDG_DATA_HOME`` as per FreeDesktop specifications, if
    exists.
    Otherwise, the ``.local/share`` directory under the user's HOME will be
    used.
    """
    basedir = os.environ.get("XDG_DATA_HOME",
                             os.path.join(os.path.expanduser('~'),
                                          ".local",
                                          "share"))
    return os.path.join(basedir, "envprobe")


def get_runtime_directory(user_id):
    """Returns a temporary directory where session-specific files can be
    stored.

    This method uses ``$XDG_RUNTIME_DIR`` as per FreeDesktop specifications, if
    exists.
    Otherwise, the system-specific temporary directory will be used.
    See :py:func:`tempfile.gettempdir` for further information.
    """
    try:
        rootdir = os.environ["XDG_RUNTIME_DIR"]
        # Use only 'envprobe' as the top-level directory because RUNTIME_DIR
        # is user-specific.
        directory = os.path.join(rootdir, "envprobe")
    except (KeyError, OSError):
        rootdir = tempfile.gettempdir()
        # Use 'envprobe-USERID' as top-level directory because the global
        # temporary directory is not user-specific.
        directory = os.path.join(rootdir, "envprobe-{0}".format(user_id))

    return directory
