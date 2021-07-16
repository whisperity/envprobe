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
from copy import deepcopy
import os
import pytest

from envprobe.commands.get import command as get_command
from envprobe.commands.descriptions import update_command
from envprobe.community_descriptions import local_data
from envprobe.library import get_shell_and_env_always
from envprobe.vartype_heuristics import ConfigurationResolvedHeuristic


@pytest.fixture(scope="module")
def args(tmp_path_factory):
    # Make a shared directory of temporary user home for the test fixture.
    tmp_path = tmp_path_factory.mktemp("test_community_descriptions")

    orig_env = deepcopy(os.environ)

    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp_path, "cfg")
    os.environ["XDG_DATA_HOME"] = os.path.join(tmp_path, "data")

    arg = Namespace()

    yield arg

    os.environ = orig_env


def test_description_update(capfd, args):
    # Assuming PATH is always part of the Variable Descriptions Project.
    # It should be, it's one of the core POSIX variables.
    vi = local_data.get_variable_information_manager("PATH")
    assert(vi["PATH"] is None)

    update_command(args)
    stdout, stderr = capfd.readouterr()
    assert("Nothing to update" not in stdout)
    assert("Extracting" in stdout)
    assert("extracted" in stdout)
    assert("Cleaning up" in stdout)
    assert("cleaned up" in stdout)
    assert(not stderr)

    update_command(args)
    stdout, stderr = capfd.readouterr()
    assert("Nothing to update" in stdout)
    assert("Extracting" not in stdout)
    assert("extracted" not in stdout)
    assert("Cleaning up" not in stdout)
    assert("cleaned up" not in stdout)
    assert(not stderr)

    vi = local_data.get_variable_information_manager("PATH")
    assert(vi["PATH"] is not None)


def test_resolution(capfd, args):
    update_command(args)

    args.VARIABLE = "PATH"
    args.info = True

    vi = local_data.get_variable_information_manager(args.VARIABLE)
    source = vi[args.VARIABLE]["source"]

    args.shell, args.environment = get_shell_and_env_always(
        os.environ,
        ConfigurationResolvedHeuristic(lambda _: vi))

    get_command(args)
    stdout, stderr = capfd.readouterr()
    assert("Source: {}".format(source) in stdout)
    assert(not stderr)
