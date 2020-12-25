from argparse import Namespace
import pytest

from envprobe.commands.undefine import command


class MockVar:
    def __init__(self, name, raw_value):
        self.name = name
        self.value = raw_value

    def raw(self):
        return self.value


class MockShell:
    def __init__(self):
        self.m_vars = ["TEST"]

    def unset_environment_variable(self, env_var):
        self.m_vars.remove(env_var.name)


class MockEnv:
    def __init__(self):
        self.vars = {"TEST": MockVar("TEST", "Foo")}

    def __getitem__(self, var_name):
        return self.vars.get(var_name, MockVar(var_name, "")), \
                var_name in self.vars

    def set_variable(self, env_var, remove=False):
        if remove:
            del self.vars[env_var.name]
        else:
            raise NotImplementedError("Not-removing is not supported!")


@pytest.fixture
def args():
    arg = Namespace()
    arg.shell = MockShell()
    arg.environment = MockEnv()

    yield arg


def test_undefine_existing(capfd, args):
    args.VARIABLE = "TEST"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert("TEST" not in args.shell.m_vars)
    assert("TEST" not in args.environment.vars)


def test_undefine_nonexistent(capfd, args):
    args.VARIABLE = "THIS DOESN'T EXIST"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert("THIS DOESN'T EXIST" not in args.shell.m_vars)
    assert("THIS DOESN'T EXIST" not in args.environment.vars)
