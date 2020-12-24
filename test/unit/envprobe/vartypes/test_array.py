import pytest

from envprobe.vartypes.colon_separated import ColonSeparatedArray
from envprobe.vartypes.semi_separated import SemicolonSeparatedArray


def test_init_and_load():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    assert(a.separator == ':')
    assert(a.value == ["Foo", "Bar"])
    assert(a.raw() == "Foo:Bar")
    assert(len(a) == 2)
    assert(a[0] == "Foo")
    assert(a[1] == "Bar")


def test_setter():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    a.value = "A:B"
    assert(a.separator == ':')
    assert(a.value == ["A", "B"])
    assert(a.raw() == "A:B")
    assert(len(a) == 2)
    assert(a[0] == "A")
    assert(a[1] == "B")


def test_setter_single():
    a = ColonSeparatedArray("test_array", "Foo")
    a.value = "42"
    assert(a.separator == ':')
    assert(a.value == ["42"])
    assert(a.raw() == "42")
    assert(len(a) == 1)
    assert(a[0] == "42")


def test_setter_other_sep():
    """
    Expect to see adding a value with ; "seperator" to be ignored and stay
    as its own element.
    """
    a = ColonSeparatedArray("test_array", "Foo")
    a.value = "A;B:Foo"
    assert(a.separator == ':')
    assert(a.value == ["A;B", "Foo"])
    assert(len(a) == 2)
    assert(a[0] == "A;B")


def test_setter_current_sep():
    """
    Expect rejecting adding a value that contains the current (:) separator.
    """
    a = ColonSeparatedArray("test_array", "Foo")

    with pytest.raises(ValueError):
        a.insert_at(-1, "Bar:Baz")

    with pytest.raises(ValueError):
        a[0] = "Foo:Bar"


def test_setitem():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    a[1] = "Baz"
    assert(a.value == ["Foo", "Baz"])

    with pytest.raises(IndexError):
        a[2] = "Qux"


def test_delitem():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    del a[0]
    assert(len(a) == 1)
    assert(a[0] == "Bar")

    del a[0]
    assert(len(a) == 0)
    assert(a.raw() == "")


def test_insert():
    a = ColonSeparatedArray("test_array", "Foo")

    # Insert at the end.
    a.insert_at(-1, "Bar")
    assert(len(a) == 2)
    assert(a[0] == "Foo")
    assert(a[1] == "Bar")

    # Insert at the beginning.
    a.insert_at(0, 42)
    assert(len(a) == 3)
    assert(a[0] == "42")
    assert(a[1] == "Foo")
    assert(a[2] == "Bar")

    # Insert as the second element.
    a.insert_at(1, "Baz")
    assert(len(a) == 4)
    assert(a[0] == "42")
    assert(a[1] == "Baz")
    assert(a[2] == "Foo")
    assert(a[3] == "Bar")

    # Insert as the second-to-last element.
    a.insert_at(-2, "Qux")
    assert(len(a) == 5)
    assert(a[0] == "42")
    assert(a[1] == "Baz")
    assert(a[2] == "Foo")
    assert(a[3] == "Qux")
    assert(a[4] == "Bar")

    assert(a.value == ["42", "Baz", "Foo", "Qux", "Bar"])


def test_remove_element():
    a = ColonSeparatedArray("test_array", "Foo:Bar")
    a.remove_value("Foo")
    assert(len(a) == 1)
    assert(a[0] == "Bar")

    a = ColonSeparatedArray("test_array", "Foo:Bar:Foo")
    a.remove_value("Foo")
    assert(len(a) == 1)
    assert(a[0] == "Bar")


def test_diff():
    a1 = ColonSeparatedArray("test_array", "Foo:Bar")
    a2 = ColonSeparatedArray("test_array", "Foo:Bar:Baz")

    diff = ColonSeparatedArray.get_difference(a1, a2)['diff']
    assert(len(diff) == 3)
    assert((' ', "Foo") in diff)
    assert((' ', "Bar") in diff)
    assert(('+', "Baz") in diff)

    a3 = ColonSeparatedArray("test_array_empty", "")
    diff = ColonSeparatedArray.get_difference(a2, a3)['diff']
    assert(len(diff) == 3)
    assert(('-', "Foo") in diff)
    assert(('-', "Bar") in diff)
    assert(('-', "Baz") in diff)


def test_semicolon():
    a = SemicolonSeparatedArray("test_array_semi", "Foo:Bar;Baz")
    assert(len(a) == 2)
    assert(a.value == ["Foo:Bar", "Baz"])
