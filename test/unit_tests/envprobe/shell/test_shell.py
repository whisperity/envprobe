import os
import pytest

from envprobe.shell.shell import get_current_shell


@pytest.fixture
def environment():
    os.environ["ENVPROBE_SHELL_TYPE"] = "false"
    yield None
    del os.environ["ENVPROBE_SHELL_TYPE"]


def test_shell_fails_to_load(environment):
    with pytest.raises(KeyError):
        get_current_shell()
