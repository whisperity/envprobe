import pytest

from envprobe.vartypes.numeric import Numeric


def test_init_and_load():
    n = Numeric("test_int", 42)
    assert(n.is_integer)
    assert(not n.is_floating)
    assert(n.value == 42)
    assert(n.raw() == "42")

    n2 = Numeric("test_float", 1.5)
    assert(not n2.is_integer)
    assert(n2.is_floating)
    assert(n2.value == 1.5)
    assert(n2.raw() == "1.5")

    n3 = Numeric("test_int_from_str", "10")
    assert(n3.is_integer)
    assert(not n3.is_floating)
    assert(n3.value == 10)
    assert(n3.raw() == "10")


def test_setter():
    n = Numeric("test_int", 42)
    n.value = 0
    assert(n.is_integer)
    assert(n.value == 0)
    assert(n.raw() == "0")


def test_setter_nonint():
    n = Numeric("test_int", 42)
    with pytest.raises(ValueError):
        n.value = "foo"


def test_diff():
    n1 = Numeric("test_int", 1)
    n2 = Numeric("test_int", 2)

    diff = Numeric.diff(n1, n2)
    assert(len(diff) == 2)
    assert(('+', "2") in diff)
    assert(('-', "1") in diff)


def test_no_diff():
    n = Numeric("test_int", 1)
    diff = Numeric.diff(n, n)
    assert(not diff)
