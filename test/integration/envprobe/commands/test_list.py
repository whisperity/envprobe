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
from argparse import Namespace
import os
import pytest

from envprobe.commands.list import command
from envprobe.settings import get_configuration_directory
from envprobe.settings.snapshot import \
    get_snapshot_directory_name as snapdir, get_snapshot_file_name as snapf


@pytest.fixture
def args(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp_path, "cfg")

    arg = Namespace()
    yield arg


def test_list(capfd, args):
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    snaproot = os.path.join(get_configuration_directory(), snapdir())
    os.makedirs(snaproot, exist_ok=True)
    os.makedirs(os.path.join(snaproot, "Foo"), exist_ok=True)
    os.makedirs(os.path.join(snaproot, "Bar", "Baz"), exist_ok=True)
    with open(os.path.join(snaproot, snapf("test1")), 'w'):
        pass
    with open(os.path.join(snaproot, snapf("test2")), 'w'):
        pass
    with open(os.path.join(snaproot, "Foo", snapf("bar")), 'w'):
        pass
    with open(os.path.join(snaproot, "Bar", snapf("thing")), 'w'):
        pass
    with open(os.path.join(snaproot, "Bar", "Baz", snapf("x")),
              'w'):
        pass

    command(args)

    stdout, stderr = capfd.readouterr()
    assert(set(filter(lambda x: x, stdout.split('\n'))) ==
           set(["test1", "test2", "Bar/thing", "Bar/Baz/x", "Foo/bar"]))
    assert(not stderr)
