import os
import pytest
import random

from envprobe.shell.shell import get_current_shell
from envprobe.vartypes.string import String


@pytest.fixture
def environment(tmp_path):
    cfg = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
           "ENVPROBE_CONFIG": str(tmp_path),
           "ENVPROBE_LOCATION": "/dummy",
           "ENVPROBE_SHELL_TYPE": "zsh"
           }
    return cfg


def test_load(environment):
    sh = get_current_shell(environment)
    assert(sh.shell_type == environment["ENVPROBE_SHELL_TYPE"])
    assert(sh.shell_pid == environment["ENVPROBE_SHELL_PID"])
    assert(sh.envprobe_location == environment["ENVPROBE_LOCATION"])
    assert(sh.configuration_directory == environment["ENVPROBE_CONFIG"])
    assert("precmd_functions" in sh.get_shell_hook())


def test_set(environment):
    sh = get_current_shell(environment)
    s = String("test", "foo")
    sh.set_env_var(s)

    with open(sh.control_file, 'r') as ctrl:
        lines = list(map(lambda x: x.strip(),
                         filter(lambda x: x != '\n', ctrl)))
        assert(len(lines) == 1)
        assert("export test=foo;" in lines)


def test_set_two(environment):
    sh = get_current_shell(environment)
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
    sh = get_current_shell(environment)
    s1 = String("test", "foo")
    sh.undefine_env_var(s1)

    with open(sh.control_file, 'r') as ctrl:
        lines = list(map(lambda x: x.strip(),
                         filter(lambda x: x != '\n', ctrl)))
        assert(len(lines) == 1)
        assert("unset test;" in lines)


def test_set_and_unset(environment):
    sh = get_current_shell(environment)
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
