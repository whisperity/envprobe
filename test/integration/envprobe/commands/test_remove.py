from argparse import Namespace
import os
import pytest

from envprobe.commands.remove import command
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
    envdict = {"PATH": "/Foo:/Bar:/Foo:/Foo:/Foo:/Bar"}

    arg = Namespace()
    arg.environment = Environment(shell, envdict, PathHeuristic())
    arg.shell = shell

    yield arg


def test_remove_path(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Bar"]
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] ==
           "/Foo:/Foo:/Foo:/Foo")


def test_remove_multiple(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["Bar", "Foo"]
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] == "")


def test_remove_nonexistent(capfd, args, cwd_to_root):
    args.VARIABLE = "PATH"
    args.VALUE = ["something"]
    command(args)

    stdout, stderr = capfd.readouterr()
    assert(not stdout)
    assert(not stderr)

    assert(args.environment.current_environment["PATH"] ==
           "/Foo:/Bar:/Foo:/Foo:/Foo:/Bar")
