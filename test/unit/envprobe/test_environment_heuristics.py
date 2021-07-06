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
import pytest

from envprobe.environment import EnvVarTypeHeuristic, HeuristicStack, \
        create_environment_variable
from envprobe.vartype_heuristics import ConfigurationResolvedHeuristic


def test_default():
    h = EnvVarTypeHeuristic()
    assert(h(None) == "string")
    assert(h("") == "string")
    assert(h("foo") == "string")


class EmptyHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        return None


class TestHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        if name == "test":
            return "test"
        if name == "break":
            return False
        return None


def test_pipeline():
    p = HeuristicStack()
    assert(p("Variable") is None)

    p += EmptyHeuristic()
    assert(p("Variable") is None)

    p += EnvVarTypeHeuristic()
    assert(p("Variable") == "string")

    p += TestHeuristic()
    assert(p("Variable") == "string")
    assert(p("test") == "test")

    p += EmptyHeuristic()
    assert(p("Variable") == "string")
    assert(p("test") == "test")

    assert(p("break") is None)


def test_pipeline_simple():
    p = HeuristicStack()
    p += EnvVarTypeHeuristic()
    p += TestHeuristic()
    assert(p("Variable") == "string")
    assert(p("test") == "test")


class NumericHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        if name not in env:
            return None

        try:
            float(env[name])
            return "numeric"
        except ValueError:
            return None


def test_creation():
    p = HeuristicStack()
    p += EnvVarTypeHeuristic()
    p += NumericHeuristic()

    env = {"variable": 5}

    num_var = create_environment_variable("variable", env, p)
    assert(num_var)
    assert(num_var.value == 5)


def test_ignore():
    p = HeuristicStack()
    p += EnvVarTypeHeuristic()
    p += TestHeuristic()

    env = {"variable": "X", "break": None}

    var = create_environment_variable("variable", env, p)
    assert(var)
    assert(var.value == env["variable"])

    with pytest.raises(KeyError):
        create_environment_variable("break", env, p)


class MockConfigurationStore:
    def __init__(self, name):
        pass

    def __getitem__(self, name):
        if name == "pathlike":
            return {'type': "path"}
        if name == "USER":
            return {'type': "string"}
        return None


def test_resolving_heuristic():
    p = HeuristicStack()
    p += ConfigurationResolvedHeuristic(MockConfigurationStore)

    assert(p("pathlike") == "path")
    assert(p("USER") == "string")
    assert(p("foo") is None)
