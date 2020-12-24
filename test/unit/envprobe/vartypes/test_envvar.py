import pytest

from envprobe import vartypes


def test_empty():
    with pytest.raises(KeyError):
        vartypes.get_class("invalid")


def test_invalid_type_fails_to_load():
    with pytest.raises(ModuleNotFoundError):
        vartypes.load("false-type")


def test_non_subtype_mock_fails():
    class X:
        pass

    with pytest.raises(TypeError):
        vartypes.register_type("X", X)


class MockVariable(vartypes.EnvVar):
    pass


def test_mock_registers_and_loads():
    with pytest.raises(KeyError):
        vartypes.get_class("fake")

    with pytest.raises(ModuleNotFoundError):
        vartypes.load("fake")

    vartypes.register_type("fake", MockVariable)
    assert(vartypes.get_class("fake") == MockVariable)

    # After registering, load() should not throw either.
    assert(vartypes.load("fake") == MockVariable)
