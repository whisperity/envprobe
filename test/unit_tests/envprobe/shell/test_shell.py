import pytest

from envprobe.shell.shell import get_current_shell


@pytest.fixture
def environment():
    cfg = {'ENVPROBE_SHELL_TYPE': "false"}
    return cfg


def test_shell_fails_to_load(environment):
    with pytest.raises(NotImplementedError):
        get_current_shell(environment)
