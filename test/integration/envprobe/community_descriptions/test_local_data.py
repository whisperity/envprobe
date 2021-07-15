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

from envprobe.community_descriptions.local_data import MetaConfiguration
from envprobe.settings.config_file import ConfigurationFile


@pytest.fixture
def tmp_json(tmp_path):
    yield os.path.join(tmp_path, "test.json")


def test_meta_uses_config_file(tmp_json):
    cfg = ConfigurationFile(tmp_json, MetaConfiguration.config_schema)
    data = MetaConfiguration(cfg)

    data.version = "TEST_VERSION"
    data.set_comment_for("foo-source", "The Comment")
    data.delete_source("nonexistent")

    cfg.save()

    cfg2 = ConfigurationFile(tmp_json, MetaConfiguration.config_schema)
    data2 = MetaConfiguration(cfg2)
    assert(data2.version == "TEST_VERSION")
    assert(data2.get_comment_for("foo-source") == "The Comment")
