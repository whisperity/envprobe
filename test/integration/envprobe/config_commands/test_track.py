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

from envprobe.config_commands.track import command, Mode, Scope
from envprobe.shell import FakeShell


class FakeShell2(FakeShell):
    def __init__(self, cfg_dir):
        self._cfg_dir = cfg_dir

    @property
    def is_envprobe_capable(self):
        return True

    @property
    def configuration_directory(self):
        return self._cfg_dir


@pytest.fixture()
def args(tmp_path):
    locald = os.path.join(tmp_path, "local")
    globald = os.path.join(tmp_path, "global")

    os.makedirs(locald)
    os.makedirs(globald)

    os.environ["XDG_CONFIG_HOME"] = globald
    shell = FakeShell2(locald)

    arg = Namespace()
    arg.default = False
    arg.shell = shell

    yield arg


def test_tracking_saves_the_config(capfd, args):
    args.VARIABLE = "FOO"
    args.scope = Scope.GLOBAL
    args.setting = Mode.IGNORE
    command(args)

    args.setting = Mode.QUERY
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("FOO: ignored" in stdout)
    assert("global explicit IGNORE" in stdout)
    assert("local explicit" not in stdout)
    assert(not stderr)

    args.VARIABLE = "BAR"
    args.scope = Scope.GLOBAL
    args.setting = Mode.IGNORE
    command(args)

    args.scope = Scope.LOCAL
    args.setting = Mode.TRACK
    command(args)

    args.setting = Mode.QUERY
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("BAR: tracked" in stdout)
    assert("local explicit TRACK" in stdout)
    assert("global explicit IGNORE" in stdout)
    assert(not stderr)


def test_default(capfd, args):
    args.VARIABLE = "FOO"
    args.scope = Scope.LOCAL
    args.setting = Mode.QUERY
    command(args)  # Query FOO, should be tracked at zero config.

    stdout, stderr = capfd.readouterr()
    assert("FOO: tracked" in stdout)
    assert("explicit" not in stdout)
    assert(not stderr)

    args.VARIABLE = None
    args.default = True
    args.setting = Mode.IGNORE
    command(args)  # Set the local default to ignore.

    args.setting = Mode.QUERY
    args.VARIABLE = "FOO"
    args.default = False
    command(args)  # Query FOO, should be ignored.

    stdout, stderr = capfd.readouterr()
    assert("FOO: ignored" in stdout)
    assert("explicit" not in stdout)
    assert(not stderr)


def test_locals_priority(capfd, args):
    args.VARIABLE = "FOO"
    args.scope = Scope.LOCAL
    args.setting = Mode.TRACK
    command(args)  # Set FOO to be tracked locally.

    args.default = True
    args.VARIABLE = None
    args.scope = Scope.GLOBAL
    args.setting = Mode.IGNORE
    command(args)  # Set the global default to ignore.

    args.default = False
    args.VARIABLE = "FOO"
    args.scope = Scope.LOCAL
    args.setting = Mode.QUERY
    command(args)  # Query FOO. Should be tracked, due to local explicit.

    stdout, stderr = capfd.readouterr()
    assert("FOO: tracked" in stdout)
    assert("local explicit TRACK" in stdout)
    assert("global explicit" not in stdout)
    assert(not stderr)

    args.VARIABLE = "BAR"
    command(args)  # Query BAR. Should be ignored due to global config.

    stdout, stderr = capfd.readouterr()
    assert("BAR: ignored" in stdout)
    assert("explicit" not in stdout)
    assert(not stderr)
