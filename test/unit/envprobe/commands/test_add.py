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
import pytest

from envprobe.commands.add import command


class MockVar:
    def __init__(self, name, raw_value):
        self.name = name
        self.value = raw_value

    def raw(self):
        return self.value


class MockEnv:
    def __getitem__(self, var_name):
        return MockVar(var_name, ""), False


@pytest.fixture
def args():
    arg = Namespace()
    arg.environment = MockEnv()

    yield arg


def test_add_not_array(args):
    with pytest.raises(TypeError):
        args.VARIABLE = "TEST"
        args.VALUE = [""]
        command(args)
