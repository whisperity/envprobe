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
The entry point if Envprobe is run as `python(3?) -m envprobe`.
"""
import os
import sys

from .main import handle_mode

if __name__ == '__main__':
    abs_path = os.path.dirname(os.path.abspath(__file__))  # .../src/envprobe
    ret = handle_mode(os.path.dirname(abs_path))  # .../src
    sys.exit(ret)
