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
Entrypoint wrappers for Envprobe when run from an install done via `pip`.
"""
import os
import sys

from envprobe.main import handle_mode


def main():
    """Entry point for the `envprobe` handler when ran from an installed
    package.
    """
    return handle_mode(os.path.dirname(sys.argv[0]))


def main_mode():
    """Entry point for the `envprobe main` handler when ran from an installed
    package.
    """
    sys.argv.insert(1, "main")
    return main()


def config_mode():
    """Entry point for the `envprobe config` handler when ran from an insatlled
    package.
    """
    sys.argv.insert(1, "config")
    return main()
