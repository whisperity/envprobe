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
from contextlib import contextmanager
import os
import sys

from libtest.envprobe import envprobe_location
from libtest.shell import Shell


@contextmanager
def bash_shell():
    """Spawns a Bash shell and provides Envprobe in the PATH."""
    envprobe_at = envprobe_location()

    with Shell("bash", "--norc --noprofile -i", "echo $?", ";\n",
               is_interactive=True) as shell:
        _, pid = shell.execute_command("echo $$")
        print("[Bash] Spawned {0}".format(pid), file=sys.stderr)

        # Make sure envprobe is not available initially.
        retcode, value = shell.execute_command("which envprobe")
        assert(retcode == 1)

        print("[Bash] Adding '{0}' to PATH...".format(envprobe_at),
              file=sys.stderr)
        shell.execute_command("export PATH=\"{0}:$PATH\"".format(envprobe_at))

        retcode, value = shell.execute_command("which envprobe")
        print("[Bash] Resolved 'envprobe' to be at '{0}'".format(value),
              file=sys.stderr)
        assert(retcode == 0)
        assert(os.path.dirname(value) == envprobe_at)

        yield shell
