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
from envprobe.settings.variable_tracking import VariableTracking


@pytest.fixture
def tmp_json(tmp_path):
    yield os.path.join(tmp_path, "test.json")


def test_track_uses_config_file(tmp_json):
    cfg = ConfigurationFile(tmp_json, VariableTracking.config_schema_global)
    vtr = VariableTracking(cfg, None)

    vtr.ignore_global("FOO")
    assert(not vtr.is_tracked("FOO"))
    assert(not vtr.is_explicitly_configured_local("FOO"))
    assert(vtr.is_explicitly_configured_global("FOO"))

    cfg.save()

    cfg2 = ConfigurationFile(tmp_json, VariableTracking.config_schema_local)
    vtr2 = VariableTracking(None, cfg2)
    assert(not vtr2.is_tracked("FOO"))
    assert(vtr2.is_explicitly_configured_local("FOO"))
    assert(not vtr2.is_explicitly_configured_global("FOO"))
