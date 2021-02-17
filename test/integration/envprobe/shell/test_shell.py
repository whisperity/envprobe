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
import random

from envprobe import shell


def test_loads_bash(tmp_path):
    environment = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
                   "ENVPROBE_CONFIG": str(tmp_path),
                   "ENVPROBE_SHELL_TYPE": 'bash'
                   }
    sh = shell.get_current_shell(environment)

    assert(sh.shell_type == environment["ENVPROBE_SHELL_TYPE"])
    assert(sh.shell_pid == environment["ENVPROBE_SHELL_PID"])
    assert(sh.configuration_directory == environment["ENVPROBE_CONFIG"])


def test_loads_zsh(tmp_path):
    environment = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
                   "ENVPROBE_CONFIG": str(tmp_path),
                   "ENVPROBE_SHELL_TYPE": 'zsh'
                   }
    sh = shell.get_current_shell(environment)

    assert(sh.shell_type == environment["ENVPROBE_SHELL_TYPE"])
    assert(sh.shell_pid == environment["ENVPROBE_SHELL_PID"])
    assert(sh.configuration_directory == environment["ENVPROBE_CONFIG"])
