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
from envprobe.settings.snapshot import Snapshot


@pytest.fixture
def tmp_json(tmp_path):
    yield os.path.join(tmp_path, "test.json")


def test_track_uses_config_file(tmp_json):
    cfg = ConfigurationFile(tmp_json, Snapshot.config_schema)
    snap = Snapshot(cfg)

    snap["FOO"] = {"XXX"}
    snap["BAR"] = ["Something"]
    snap["NUM"] = 8
    del snap["UNDEFINE"]

    cfg.save()

    cfg2 = ConfigurationFile(tmp_json, Snapshot.config_schema)
    snap2 = Snapshot(cfg2)
    assert(snap2["FOO"] == {"XXX"})
    assert(snap2["BAR"] == ["Something"])
    assert(snap2["NUM"] == 8)
    assert(snap2["UNDEFINE"] is snap2.UNDEFINE)
    assert(snap2["UNDEFINE"] is not snap.UNDEFINE)  # UNDEFINE tag is unique!
    assert(snap2["NEVER EXISTED"] is None)
