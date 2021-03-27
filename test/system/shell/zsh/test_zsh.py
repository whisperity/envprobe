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
from glob import glob
import os
import pytest

from .helper import zsh_shell
from libtest.envprobe import envprobe_location


@pytest.fixture(scope='module')
def sh():
    with zsh_shell() as sh:
        yield sh


def test_envprobe_loaded(sh, tmp_path):
    retcode, _ = sh.execute_command("export XDG_DATA_HOME=\"{0}/data\" "
                                    "XDG_CONFIG_HOME=\"{0}/config\" "
                                    "XDG_RUNTIME_DIR=\"{0}/runtime\""
                                    .format(os.path.dirname(tmp_path)))
    assert(not retcode)

    retcode, _ = sh.execute_command("envprobe --help", timeout=1)
    assert(not retcode)

    _, hook_text = sh.execute_command("envprobe config hook zsh $$",
                                      timeout=2)
    assert("envprobe" in hook_text)
    assert("precmd_functions" in hook_text)

    sh.execute_command("""_HOOK=$(cat <<'EOF'
{0}
EOF
)""".format(hook_text))

    retcode, _ = sh.execute_command("eval \"$_HOOK\"", timeout=2)
    assert(not retcode)


def test_alias(sh):
    _, result = sh.execute_command("alias")
    assert("ep=envprobe" in result)
    assert("epc=envprobe-config" in result)


def test_get_variable(sh):
    retcode, _ = sh.execute_command("envprobe get", timeout=0.5)
    assert(retcode == 2)

    retcode, result = sh.execute_command("envprobe get PATH",
                                         timeout=0.5)
    assert(not retcode)
    assert(result.startswith("PATH={0}".format(envprobe_location())))

    retcode, result = sh.execute_command("envprobe get ENVPROBE_SHELL_PID",
                                         timeout=0.5)
    assert(retcode == 1)

    retcode, result = sh.execute_command("ep PATH", timeout=0.5)
    assert(not retcode)
    assert(result.startswith("PATH={0}".format(envprobe_location())))

    retcode, result = sh.execute_command("ep \'?PATH\'", timeout=0.5)
    assert(not retcode)
    assert(result.startswith("PATH={0}".format(envprobe_location())))


def test_set_variable(sh):
    retcode, _ = sh.execute_command("envprobe set SOMETHING", timeout=0.5)
    assert(retcode == 2)

    _, result = sh.execute_command("echo $DUMMY_VAR $DUMMY_PATH")
    assert(not result)

    retcode, result = sh.execute_command("envprobe set DUMMY_VAR test",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "test")

    retcode, result = sh.execute_command("envprobe set DUMMY_PATH /mnt",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_PATH")
    assert(result == "/mnt")

    retcode, result = sh.execute_command("ep DUMMY_VAR=system", timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "system")

    retcode, result = sh.execute_command("ep \'!DUMMY_VAR\' shortcut",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "shortcut")


def test_undefine_variable(sh):
    retcode, result = sh.execute_command("envprobe undefine NON_EXISTING_VAR",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)

    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "shortcut")

    retcode, result = sh.execute_command("ep undefine DUMMY_VAR", timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(not result)

    retcode, result = sh.execute_command("ep ^DUMMY_PATH", timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_PATH")
    assert(not result)


def test_add_and_remove(sh, tmp_path):
    retcode, result = sh.execute_command("pwd")
    assert(not retcode)
    old_wd = result
    retcode, _ = sh.execute_command("cd \"{0}\"".format(tmp_path))
    assert(not retcode)
    retcode, _ = sh.execute_command("mkdir dummy")
    assert(not retcode)
    retcode, _ = sh.execute_command("echo 'echo \"Hello\"' > dummy/exe")
    assert(not retcode)
    retcode, _ = sh.execute_command("chmod +x dummy/exe")
    assert(not retcode)

    retcode, result = sh.execute_command("which exe")
    assert(retcode == 1)
    assert(result == "exe not found")

    retcode, result = sh.execute_command("ep +PATH dummy", timeout=0.5)
    assert(not retcode)
    assert(not result)
    retcode, result = sh.execute_command("which exe")
    assert(not retcode)
    assert(result == os.path.join(tmp_path, "dummy/exe"))

    retcode, result = sh.execute_command("ep remove PATH dummy", timeout=0.5)
    assert(not retcode)
    assert(not result)
    retcode, result = sh.execute_command("which exe")
    assert(retcode == 1)
    assert(result == "exe not found")

    retcode, _ = sh.execute_command("cd \"{0}\"".format(old_wd))
    assert(not retcode)


def test_diff(sh):
    retcode, result = sh.execute_command("envprobe diff", timeout=0.5)
    assert(not retcode)
    assert(result)
    retcode, result = sh.execute_command("ep %", timeout=0.5)
    assert(not retcode)
    assert(result)

    retcode, result = sh.execute_command("ep FOOBAR=xyz", timeout=0.5)
    assert(not retcode)
    assert(not result)
    retcode, result = sh.execute_command("ep +DUMMY_PATH .", timeout=0.5)
    assert(not retcode)
    assert(not result)

    retcode, result = sh.execute_command("pwd")
    assert(not retcode)
    pwd = result

    retcode, result = sh.execute_command("ep % FOOBAR DUMMY_PATH NOT_CHANGED",
                                         timeout=0.5)
    assert(not retcode)
    expected = ["(+) Added:       DUMMY_PATH",
                "\tdefined value: ['{0}']".format(pwd),
                "(+) Added:       FOOBAR",
                "\tdefined value: xyz"
                ]
    assert(result)
    assert(list(filter(lambda x: x, result.splitlines(False))) == expected)

    retcode, result = sh.execute_command("ep ^FOOBAR", timeout=0.5)
    assert(not retcode)
    assert(not result)
    retcode, result = sh.execute_command("ep ^DUMMY_PATH", timeout=0.5)
    assert(not retcode)
    assert(not result)

    retcode, result = sh.execute_command("ep % FOOBAR DUMMY_PATH NOT_CHANGED",
                                         timeout=0.5)
    assert(not retcode)
    assert(list(filter(lambda x: x, result.splitlines(False))) == [])


def test_save(sh):
    retcode, result = sh.execute_command("pwd")
    assert(not retcode)
    old_wd = result
    retcode, _ = sh.execute_command("cd /")
    assert(not retcode)

    retcode, result = sh.execute_command("ep +DUMMY_PATH Foo", timeout=0.5)
    assert(not retcode)
    assert(not result)

    retcode, result = sh.execute_command("ep save dummy_path DUMMY_PATH",
                                         timeout=0.5)
    assert(not retcode)
    assert(list(filter(lambda x: x, result.splitlines(False))) ==
           ["New variable 'DUMMY_PATH' with value '['/Foo']'."])

    retcode, result = sh.execute_command("ep +DUMMY_PATH Bar", timeout=0.5)
    assert(not retcode)
    assert(not result)

    # Simulate oversaving. This will save both /Foo and /Bar to the save file,
    # hopefully. Testing this will happen with the testing of load().
    retcode, result = sh.execute_command("ep save dummy_path DUMMY_PATH",
                                         timeout=0.5)
    assert(not retcode)
    assert(list(filter(lambda x: x, result.splitlines(False))) ==
           ["For variable 'DUMMY_PATH' the element '/Bar' was added."])

    retcode, _ = sh.execute_command("cd \"{0}\"".format(old_wd))
    assert(not retcode)

    retcode, result = sh.execute_command("ep ^DUMMY_PATH", timeout=0.5)
    assert(not retcode)
    assert(not result)


def test_load(sh):
    retcode, result = sh.execute_command("ep set DUMMY_PATH /", timeout=0.5)
    assert(not retcode)
    assert(not result)

    retcode, result = sh.execute_command("ep load dummy_path", timeout=0.5)
    assert(not retcode)
    assert(list(filter(lambda x: x, result.splitlines(False))) ==
           ["For variable 'DUMMY_PATH' the element '/Foo' will be added.",
            "For variable 'DUMMY_PATH' the element '/Bar' will be added."])

    retcode, result = sh.execute_command("ep \'?DUMMY_PATH\'", timeout=0.5)
    assert(not retcode)
    assert(result == "DUMMY_PATH=/Foo:/Bar:/")

    retcode, result = sh.execute_command("ep ^DUMMY_PATH", timeout=0.5)
    assert(not retcode)
    assert(not result)


def test_exit(sh):
    retcode, result = sh.execute_command("echo $XDG_RUNTIME_DIR")
    assert(not retcode)
    tempdir = result

    assert(any(str(sh.pid) in f for f in glob(os.path.join(tempdir, "**"),
                                              recursive=True)))

    try:
        retcode, result = sh.execute_command("exit")
    except ValueError:
        # Ignore the error. The shell exited, of course we could not gather a
        # return status.
        pass

    assert(not all(str(sh.pid) in f for f in glob(os.path.join(tempdir, "**"),
                                                  recursive=True)))
