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
from envprobe.settings.variable_information import VariableInformation


MOCK_DESCRIPTION = "This is a mock object."


class MockExtendedData:
    @property
    def type(self):
        return "mock"

    @property
    def description(self):
        return MOCK_DESCRIPTION


def test_setup():
    i = VariableInformation()
    assert(i["FOO"] is None)
    assert(not i.keys())


def test_set_and_get():
    i = VariableInformation()
    i.set("FOO", MockExtendedData(), "test")

    print(i["FOO"])

    assert(i["FOO"]["description"] == MOCK_DESCRIPTION)
    assert(i["FOO"]["type"] == "mock")
    assert(i["FOO"]["source"] == "test")

    assert(i["BAR"] is None)
    assert(i.keys() == {"FOO"})


def test_delete():
    i = VariableInformation()
    i.set("FOO", MockExtendedData(), "test")
    del i["FOO"]

    assert(i["FOO"] is None)
    assert(i["BAR"] is None)
    assert(not i.keys())
