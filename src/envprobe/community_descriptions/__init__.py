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
"""This package contains the routines that allow Envprobe to interface with the
"Envprobe Variable Descriptions Knowledge Base" project.

This sister project of Envprobe allows sharing type, description, and usage
information with the users for variables that are common across systems.
"""
from . import downloader, local_data

__all__ = [
    'downloader',
    'local_data'
]
