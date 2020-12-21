import os
import pytest
import random

from envprobe.shell.shell import get_current_shell
from envprobe.vartypes.string import String


@pytest.fixture
def environment(tmp_path):
    cfg = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
           "ENVPROBE_CONFIG": str(tmp_path),
           "ENVPROBE_SHELL_TYPE": "zsh"
           }
    return cfg


def _control_lines(shell):
    with open(shell.control_file, 'r') as cfile:
        return list(map(lambda x: x.strip(),
                        filter(lambda x: x != '\n', cfile)))


def test_load(environment):
    sh = get_current_shell(environment)
    assert(sh.shell_type == environment["ENVPROBE_SHELL_TYPE"])
    assert(sh.shell_pid == environment["ENVPROBE_SHELL_PID"])
    assert(sh.configuration_directory == environment["ENVPROBE_CONFIG"])
    assert(os.path.basename(sh.control_file) == "control.zsh")
    assert(sh.is_envprobe_capable)
    assert(sh.manages_environment_variables)
    assert("precmd_functions" in sh.get_shell_hook())


def test_set(environment):
    sh = get_current_shell(environment)
    s = String("test", "foo")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export test=foo;" in lines)


def test_set_two(environment):
    sh = get_current_shell(environment)
    s1 = String("test", "foo")
    s2 = String("test2", "bar")
    sh.set_environment_variable(s1)
    sh.set_environment_variable(s2)

    lines = _control_lines(sh)
    assert("export test=foo;" in lines)
    assert("export test2=bar;" in lines)


def test_set_pathy(environment):
    sh = get_current_shell(environment)
    s = String("test_path", "Foo:Bar")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export test_path=Foo:Bar;" in lines)


def test_set_spacey(environment):
    sh = get_current_shell(environment)
    s = String("has_spaces", "a b")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export has_spaces='a b';" in lines)


def test_unset(environment):
    sh = get_current_shell(environment)
    s1 = String("test", "foo")
    sh.unset_environment_variable(s1)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("unset test;" in lines)


def test_set_and_unset(environment):
    sh = get_current_shell(environment)
    s1 = String("test", "foo")
    s2 = String("test2", "bar")
    sh.set_environment_variable(s1)
    sh.unset_environment_variable(s2)

    lines = _control_lines(sh)
    assert(len(lines) == 2)
    assert("export test=foo;" in lines)
    assert("unset test2;" in lines)
