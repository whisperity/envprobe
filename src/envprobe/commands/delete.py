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
import sys

from envprobe.settings import get_configuration_directory
from envprobe.settings.snapshot import get_snapshot_directory_name, \
    get_snapshot_file_name


name = 'delete'
description = \
    """Delete a saved snapshot."""
help = "Delete a saved snapshot."


def command(args):
    snapshot_file = os.path.join(get_configuration_directory(),
                                 get_snapshot_directory_name(),
                                 get_snapshot_file_name(args.SNAPSHOT))

    if not os.path.isfile(snapshot_file):
        print("No snapshot named '{0}'.".format(args.SNAPSHOT),
              file=sys.stderr)
        return 1

    os.unlink(snapshot_file)


def register(argparser, shell):
    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help
    )

    parser.add_argument('SNAPSHOT',
                        type=str,
                        help="The name of the snapshot to delete.")
    parser.set_defaults(func=command)
