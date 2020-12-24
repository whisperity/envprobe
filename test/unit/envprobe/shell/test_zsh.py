import os
import pytest
import random

from envprobe.shell.zsh import Zsh


class MockVar:
    def __init__(self, var_name, value):
        self.name = var_name
        self.value = value

    def to_raw_var(self):
        return self.value


@pytest.fixture
def sh(tmp_path):
    return Zsh(random.randint(1024, 65536), str(tmp_path))


def _control_lines(shell):
    with open(shell.control_file, 'r') as cfile:
        return list(map(lambda x: x.strip(),
                        filter(lambda x: x != '\n', cfile)))


def test_load(sh):
    assert(os.path.basename(sh.control_file) == "control.zsh")
    assert(sh.is_envprobe_capable)
    assert(sh.manages_environment_variables)
    assert("precmd_functions" in sh.get_shell_hook(""))


def test_set(sh):
    s = MockVar("test", "foo")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export test=foo;" in lines)


def test_set_two(sh):
    s1 = MockVar("test", "foo")
    s2 = MockVar("test2", "bar")
    sh.set_environment_variable(s1)
    sh.set_environment_variable(s2)

    lines = _control_lines(sh)
    assert("export test=foo;" in lines)
    assert("export test2=bar;" in lines)


def test_set_pathy(sh):
    s = MockVar("test_path", "Foo:Bar")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export test_path=Foo:Bar;" in lines)


def test_set_spacey(sh):
    s = MockVar("has_spaces", "a b")
    sh.set_environment_variable(s)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("export has_spaces='a b';" in lines)


def test_unset(sh):
    s1 = MockVar("test", "foo")
    sh.unset_environment_variable(s1)

    lines = _control_lines(sh)
    assert(len(lines) == 1)
    assert("unset test;" in lines)


def test_set_and_unset(sh):
    s1 = MockVar("test", "foo")
    s2 = MockVar("test2", "bar")
    sh.set_environment_variable(s1)
    sh.unset_environment_variable(s2)

    lines = _control_lines(sh)
    assert(len(lines) == 2)
    assert("export test=foo;" in lines)
    assert("unset test2;" in lines)
