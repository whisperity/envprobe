from argparse import Namespace
import pytest

from envprobe.commands.add import command


class MockVar:
    def __init__(self, name, raw_value):
        self.name = name
        self.value = raw_value

    def raw(self):
        return self.value


class MockEnv:
    def __getitem__(self, var_name):
        return MockVar(var_name, ""), False


@pytest.fixture
def args():
    arg = Namespace()
    arg.environment = MockEnv()

    yield arg


def test_add_not_array(args):
    with pytest.raises(TypeError):
        args.VARIABLE = "TEST"
        args.VALUE = [""]
        command(args)
