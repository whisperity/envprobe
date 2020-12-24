import pytest

from envprobe import shell


def test_empty_environment():
    with pytest.raises(KeyError):
        shell.get_current_shell({})


def test_unknown_fails_to_load():
    with pytest.raises(ModuleNotFoundError):
        shell.get_current_shell({"ENVPROBE_SHELL_TYPE": "false"})


def test_mock_registers_and_loads():
    with pytest.raises(KeyError):
        shell.get_class('fake')

    with pytest.raises(ModuleNotFoundError):
        shell.load('fake')

    shell.register_type('fake', shell.FakeShell)
    assert(shell.get_class('fake') == shell.FakeShell)

    # After registering, load() should not throw.
    assert(shell.load('fake') == shell.FakeShell)
