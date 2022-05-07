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

from envprobe.settings import get_configuration_directory
from envprobe.settings.snapshot import get_snapshot_directory_name, \
    get_snapshot_name


name = 'list'
description = \
    """List the names of saved snapshots."""
help = "List the names of the saved snapshots."


def command(args):
    snapshot_save_location = os.path.join(get_configuration_directory(),
                                          get_snapshot_directory_name())
    for subdir, _, files in os.walk(snapshot_save_location):
        for file in sorted(files):
            file_path = os.path.relpath(os.path.join(subdir, file),
                                        snapshot_save_location)
            snapshot_name = get_snapshot_name(file_path)
            if snapshot_name:
                print(snapshot_name)


def register(argparser, shell):
    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.set_defaults(func=command)
