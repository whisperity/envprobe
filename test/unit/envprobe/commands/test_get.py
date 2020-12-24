from argparse import Namespace
import pytest

from envprobe.commands.get import command


class MockVar:
    def __init__(self, name, raw_value):
        self.name = name
        self.value = raw_value

    def raw(self):
        return self.value


class MockCommunity:
    def get_description(self, var_name):
        return dict()


class MockEnv:
    def __init__(self):
        self.vars = {"TEST": MockVar("TEST", "Foo"),
                     "COMMUNITY": MockVar("COMMUNITY", "yes")
                     }

    def __getitem__(self, var_name):
        return self.vars.get(var_name, MockVar(var_name, "")), \
                var_name in self.vars


@pytest.fixture
def args():
    arg = Namespace()
    arg.community = MockCommunity()
    arg.environment = MockEnv()

    yield arg


def test_get_existing(capfd, args):
    args.VARIABLE = "TEST"
    args.info = False
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(stdout.rstrip() == "TEST=Foo")
    assert(not stderr)


def test_get_nonexistent(capfd, args):
    args.VARIABLE = "THIS DOESN'T EXIST"
    args.info = False
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(stderr.rstrip() == "THIS DOESN'T EXIST is not defined")


def test_info_builtin(capfd, args):
    args.VARIABLE = "TEST"
    args.info = True
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("Type: 'unknown'" in stdout)
    assert("test_get.MockVar" in stdout)
    assert("Description" not in stdout)
    assert("Source" not in stdout)
    assert(not stderr)


# TODO: Implement this one.
def TODO_test_info_community(capfd, args):
    args.VARIABLE = "COMMUNITY"
    args.info = True
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("Type: 'unknown'" in stdout)
    assert("test_get.MockVar" in stdout)
    assert("Description" in stdout)
    assert("Source" in stdout)
    assert(not stderr)
