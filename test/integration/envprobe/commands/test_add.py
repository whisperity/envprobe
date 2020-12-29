from argparse import Namespace
import os
import pytest

from envprobe.commands.add import command
from envprobe.environment import Environment
from envprobe.shell import FakeShell


class FakeShell2(FakeShell):
    @property
    def manages_environment_variables(self):
        return True

    def _set_environment_variable(self, env_var):
        pass


class PathHeuristic:
    def __call__(self, name, env=None):
        return 'path'


@pytest.fixture
def cwd_to_root():
    wd = os.getcwd()
    os.chdir("/")
    yield None  # Allow running of the test code.
    os.chdir(wd)


@pytest.fixture
def args():
    shell = FakeShell2()
    envdict = {"PATH": "/Foo:/Bar"}

    arg = Namespace()
    arg.environment = Environment(shell, envdict, PathHeuristic())
    arg.shell = shell

    yield arg


def test_add_path_prefix(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Baz"]
    args.position = 0
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] == "/Baz:/Foo:/Bar")


def test_add_path_postfix(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Qux"]
    args.position = -1
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] == "/Foo:/Bar:/Qux")


def test_add_multiple(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Baz", "Qux"]
    args.position = 0
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] ==
           "/Baz:/Qux:/Foo:/Bar")


def test_add_multiple_negative(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Baz", "Qux"]
    args.position = -2
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] ==
           "/Foo:/Baz:/Qux:/Bar")


def test_add_to_new_variable(capfd, args, cwd_to_root):
    args.VARIABLE = "NEW_PATH"
    args.VALUE = ["root"]
    args.position = 0
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)
    assert(args.environment.current_environment["NEW_PATH"] == "/root")

    # The other variable should be unchanged.
    assert(args.environment.current_environment["PATH"] == "/Foo:/Bar")
