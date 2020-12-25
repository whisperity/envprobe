from argparse import Namespace
import pytest

from envprobe.commands.set import command


class MockVar:
    def __init__(self, name, raw_value):
        self.name = name
        self.value = raw_value

    def raw(self):
        return self.value


class MockShell:
    def __init__(self):
        self.m_vars = list()

    def set_environment_variable(self, env_var):
        self.m_vars.append(env_var.name)


class MockEnv:
    def __init__(self):
        self.vars = {"TEST": MockVar("TEST", "Foo")}

    def __getitem__(self, var_name):
        return self.vars.get(var_name, MockVar(var_name, "")), \
                var_name in self.vars

    def apply_change(self, env_var):
        self.vars[env_var.name] = env_var.raw()


@pytest.fixture
def args():
    arg = Namespace()
    arg.shell = MockShell()
    arg.environment = MockEnv()

    yield arg


def test_set_existing(capfd, args):
    args.VARIABLE = "TEST"
    args.VALUE = "Bar"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert("TEST" in args.shell.m_vars)
    assert(args.environment.vars["TEST"] == "Bar")


def test_set_nonexistent(capfd, args):
    args.VARIABLE = "THIS DOESN'T EXIST"
    args.VALUE = "Something"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert("THIS DOESN'T EXIST" in args.shell.m_vars)
    assert(args.environment.vars["THIS DOESN'T EXIST"] == "Something")
