import pytest

from envprobe.vartypes.numeric import Numeric


def test_init_and_load():
    n = Numeric("test_int", 42)
    assert(n.is_integer)
    assert(not n.is_floating)
    assert(n.value == 42)
    assert(n.to_raw_var() == "42")

    n2 = Numeric("test_float", 1.5)
    assert(not n2.is_integer)
    assert(n2.is_floating)
    assert(n2.value == 1.5)
    assert(n2.to_raw_var() == "1.5")


def test_setter():
    n = Numeric("test_int", 42)
    n.value = 0
    assert(n.is_integer)
    assert(n.value == 0)
    assert(n.to_raw_var() == "0")


def test_setter_nonint():
    n = Numeric("test_int", 42)
    with pytest.raises(ValueError):
        n.value = "foo"


def test_diff():
    n1 = Numeric("test_int", 1)
    n2 = Numeric("test_int", 2)

    diff = Numeric.get_difference(n1, n2)
    assert(diff['type'] == "Numeric")
    assert(len(diff['diff']) == 2)
    assert(('+', "2") in diff['diff'])
    assert(('-', "1") in diff['diff'])
