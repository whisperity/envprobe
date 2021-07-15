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
import csv
import pytest
import os

from envprobe.community_descriptions.downloader import DescriptionSource


@pytest.fixture
def csv_source(tmp_path):
    fields = ["Variable", "TypeKind", "Description"]
    path = os.path.join(tmp_path, "data.csv")

    with open(path, 'w') as handle:
        writer = csv.DictWriter(handle, fields)

        writer.writeheader()
        writer.writerow({"Variable": "__META__",
                         "TypeKind": "COMMENT",
                         "Description": "This is the comment."})
        writer.writerow({"Variable": "__INVALID__",
                         "TypeKind": "???",
                         "Description": "!!!"})
        writer.writerow({"Variable": "MY_VAR",
                         "TypeKind": "string",
                         "Description": "foo"})

    yield path


def test_description_source_parsing(csv_source):
    p = DescriptionSource(csv_source)

    assert(p.name == "data")
    assert(len(p) == 0)

    p.parse()

    assert(len(p) == 2)
    assert(p["MY_VAR"] is not None)
    assert(p["__INVALID__"] is not None)

    with pytest.raises(KeyError):
        p["__META__"]
