from argparse import Namespace
import pytest

from envprobe.commands.get import command
from envprobe.vartypes.path import PathLike


class MockCommunity:
    def get_description(self, var_name):
        return dict()


class MockEnv:
    def __init__(self):
        self.vars = {"PATH1": PathLike("PATH1", "/Foo:/Bar"),
                     "PATH_EMPTY": PathLike("PATH_EMPTY", "")
                     }

    def __getitem__(self, var_name):
        return self.vars.get(var_name), var_name in self.vars


@pytest.fixture
def args():
    arg = Namespace()
    arg.community = MockCommunity()
    arg.environment = MockEnv()
    arg.info = True

    yield arg


def test_get_path_breakdown(capfd, args):
    args.VARIABLE = "PATH1"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("PATH1=/Foo:/Bar" in stdout)
    assert("PATH1:\n\t/Foo\n\t/Bar" in stdout)
    assert(not stderr)


def test_get_path_empty(capfd, args):
    args.VARIABLE = "PATH_EMPTY"
    command(args)

    stdout, stderr = capfd.readouterr()
    assert("PATH_EMPTY=" in stdout)
    assert("PATH_EMPTY:\n --- empty ---" in stdout)
    assert(not stderr)
