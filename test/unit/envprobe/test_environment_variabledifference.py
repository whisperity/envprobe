from envprobe.environment import VariableDifference
from envprobe.environment import VariableDifferenceKind as VDK


def test_diff_new():
    diff = VariableDifference(VDK.ADDED, "X", None, "Bar",
                              [('+', "Bar")])
    assert(diff.is_simple_change)
    assert(diff.is_new)
    assert(not diff.is_unset)


def test_diff_del():
    diff = VariableDifference(VDK.REMOVED, "X", "Foo", None,
                              [('-', "Foo")])
    assert(diff.is_simple_change)
    assert(not diff.is_new)
    assert(diff.is_unset)


def test_diff_simple():
    diff = VariableDifference(VDK.CHANGED, "X", "Foo", "Bar",
                              [('+', "Bar"), ('-', "Foo")])
    assert(diff.is_simple_change)
    assert(not diff.is_new)
    assert(not diff.is_unset)


def test_diff_not_simple():
    diff = VariableDifference(VDK.CHANGED, "PATH", "/x:/y", "/x:/z",
                              [('=', "/x"),
                               ('+', "/z"),
                               ('-', "/y")
                               ])
    assert(not diff.is_simple_change)
    assert(not diff.is_new)
    assert(not diff.is_unset)
