import os
import pytest
import random

from envprobe.shell.shell import get_current_shell
from envprobe.vartypes.string import String


@pytest.fixture
def environment(tmp_path):
    cfg = {'pid': str(random.randint(1024, 65536)),
           'cfg': str(tmp_path),
           'dir': "/dummy",
           'type': "zsh"
           }

    os.environ["ENVPROBE_SHELL_TYPE"] = cfg["type"]
    os.environ["ENVPROBE_SHELL_PID"] = cfg["pid"]
    os.environ["ENVPROBE_LOCATION"] = cfg["dir"]
    os.environ["ENVPROBE_CONFIG"] = cfg["cfg"]

    yield cfg

    del os.environ["ENVPROBE_CONFIG"]
    del os.environ["ENVPROBE_LOCATION"]
    del os.environ["ENVPROBE_SHELL_PID"]
    del os.environ["ENVPROBE_SHELL_TYPE"]


def test_load(environment):
    sh = get_current_shell()
    assert(sh.shell_type == environment["type"])
    assert(sh.shell_pid == environment["pid"])
    assert(sh.envprobe_location == environment["dir"])
    assert(sh.configuration_directory == environment["cfg"])
    assert("precmd_functions" in sh.get_shell_hook())


def test_set(environment):
    sh = get_current_shell()
    s = String("test", "foo")
    sh.set_env_var(s)

    with open(sh.control_file, 'r') as ctrl:
        lines = list(map(lambda x: x.strip(),
                         filter(lambda x: x != '\n', ctrl)))
        assert(len(lines) == 1)
        assert("export test=foo;" in lines)


def test_set_two(environment):
    sh = get_current_shell()
    s1 = String("test", "foo")
    s2 = String("test2", "bar")
    sh.set_env_var(s1)
    sh.set_env_var(s2)

    with open(sh.control_file, 'r') as ctrl:
        lines = list(map(lambda x: x.strip(),
                         filter(lambda x: x != '\n', ctrl)))
        assert(len(lines) == 2)
        assert("export test=foo;" in lines)
        assert("export test2=bar;" in lines)


def test_unset(environment):
    sh = get_current_shell()
    s1 = String("test", "foo")
    sh.undefine_env_var(s1)

    with open(sh.control_file, 'r') as ctrl:
        lines = list(map(lambda x: x.strip(),
                         filter(lambda x: x != '\n', ctrl)))
        assert(len(lines) == 1)
        assert("unset test;" in lines)


def test_set_and_unset(environment):
    sh = get_current_shell()
    s1 = String("test", "foo")
    s2 = String("test2", "bar")
    sh.set_env_var(s1)
    sh.undefine_env_var(s2)

    with open(sh.control_file, 'r') as ctrl:
        lines = list(map(lambda x: x.strip(),
                         filter(lambda x: x != '\n', ctrl)))
        assert(len(lines) == 2)
        assert("export test=foo;" in lines)
        assert("unset test2;" in lines)
