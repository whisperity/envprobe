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
import pytest

from envprobe.settings.config_file import ConfigurationFile
from envprobe.settings.variable_information import VariableInformation
from envprobe.vartypes.envvar import EnvVarExtendedInformation


@pytest.fixture
def tmp_json(tmp_path):
    yield os.path.join(tmp_path, "test.json")


def test_track_uses_config_file(tmp_json):
    cfg = ConfigurationFile(tmp_json, VariableInformation.config_schema)
    info = VariableInformation(cfg)

    extended = EnvVarExtendedInformation()
    extended.description = "Test description"
    extended._type = "type1"
    info.set("FOO", extended, "test")

    cfg.save()

    cfg2 = ConfigurationFile(tmp_json, VariableInformation.config_schema)
    info2 = VariableInformation(cfg2)
    assert(info2["FOO"]["type"] == "type1")
    assert(info2["FOO"]["source"] == "test")
    assert(info2["FOO"]["description"] == "Test description")
    assert(info2["NEVER EXISTED"] is None)
