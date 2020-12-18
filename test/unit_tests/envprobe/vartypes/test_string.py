from envprobe.vartypes.string import String


def test_init_and_load():
    s = String("test_string", "foo")
    assert(s.value == "foo")
    assert(s.to_raw_var() == "foo")


def test_setter():
    s = String("test_string", "foo")
    s.value = "bar"
    assert(s.value == "bar")
    assert(s.to_raw_var() == "bar")


def test_setter_nonstring():
    s = String("test_string", "foo")
    s.value = 42
    assert(type(s.value) == str)
    assert(s.value == "42")


def test_diff():
    s1 = String("test_string", "foo")
    s2 = String("test_string", "foo")
    s2.value = "bar"

    diff = String.get_difference(s1, s2)
    assert(diff['type'] == "String")
    assert(len(diff['diff']) == 2)
    assert(('+', "bar") in diff['diff'])
    assert(('-', "foo") in diff['diff'])


def test_diff_new():
    s1 = String("test_string", "")
    s2 = String("test_string", "bar")

    diff = String.get_difference(s1, s2)
    assert(len(diff['diff']) == 1)
    assert(('+', "bar") in diff['diff'])


def test_diff_remove():
    s1 = String("test_string", "")
    s2 = String("test_string", "bar")

    diff = String.get_difference(s2, s1)
    assert(len(diff['diff']) == 1)
    assert(('-', "bar") in diff['diff'])
