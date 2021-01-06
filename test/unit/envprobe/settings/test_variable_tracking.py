import pytest

from envprobe.compatibility import nullcontext
from envprobe.settings.variable_tracking import VariableTracking


def test_setup():
    t = VariableTracking()
    assert(t.is_tracked("FOO"))


def test_defaults():
    t = VariableTracking()
    t.local_tracking = False
    t.global_tracking = False

    assert(not t.is_tracked("FOO"))

    t.local_tracking = True

    assert(t.is_tracked("FOO"))


def test_local():
    t = VariableTracking()
    t.ignore_local("FOO")
    assert(t.is_explicitly_configured_local("FOO"))
    assert(not t.is_explicitly_configured_global("FOO"))
    assert(not t.is_tracked("FOO"))

    t.unset_local("FOO")
    assert(not t.is_explicitly_configured_local("FOO"))
    assert(not t.is_explicitly_configured_global("FOO"))
    assert(t.is_tracked("FOO"))


def test_global():
    t = VariableTracking()
    t.ignore_global("FOO")
    assert(not t.is_explicitly_configured_local("FOO"))
    assert(t.is_explicitly_configured_global("FOO"))
    assert(not t.is_tracked("FOO"))

    t.unset_global("FOO")
    assert(not t.is_explicitly_configured_local("FOO"))
    assert(not t.is_explicitly_configured_global("FOO"))
    assert(t.is_tracked("FOO"))


def test_unset_not_set():
    t = VariableTracking()
    t.unset_local("FOO")
    t.unset_global("BAR")

    assert(t.is_tracked("FOO"))
    assert(t.is_tracked("BAR"))


def test_overlay():
    t = VariableTracking()
    t.local_tracking = False

    t.track_local("LOCAL_TRACKED")
    t.ignore_global("GLOBAL_IGNORED")

    assert(t.is_tracked("DEFAULT", "LOCAL_TRACKED", "GLOBAL_IGNORED")
           == [False, True, False])

    t.global_tracking = False

    t.ignore_local("LOCAL_IGNORED")
    t.track_global("GLOBAL_TRACKED")

    assert(t.is_tracked("DEFAULT", "LOCAL_TRACKED", "LOCAL_IGNORED",
                        "GLOBAL_TRACKED", "GLOBAL_IGNORED")
           == [False, True, False, True, False])


def test_unconfigured():
    L = nullcontext(dict())
    G = nullcontext(dict())

    t = VariableTracking(L, G)

    assert(t.default_tracking is True)
    assert(t.local_tracking is None)
    assert(t.global_tracking is True)

    assert(t.is_tracked("FOO"))

    t.global_tracking = False

    assert(t.default_tracking is False)

    assert(not t.is_tracked("FOO"))

    with pytest.raises(KeyError):
        t.track_local("FOO")
