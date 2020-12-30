import io
import json
import os
import pytest

from envprobe.settings.config_file import ConfigurationFile


@pytest.fixture
def tmp(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path  # Allow the tests to run.
    os.chdir(cwd)


def test_load_empty(tmp):
    c = ConfigurationFile("test.json")
    assert(not c._data)
    assert(len(c) == 0)
    assert(not os.path.isfile("test.json"))

    c.load()
    assert(not c._data)
    assert(len(c) == 0)
    assert(not os.path.isfile("test.json"))


def test_save_empty(tmp):
    c = ConfigurationFile("test.json")
    c.save()
    assert(not os.path.isfile("test.json"))


def test_load_default(tmp):
    c = ConfigurationFile("test.json", {"Default": True})
    assert(len(c) == 1)
    assert(c["Default"] is True)
    assert(not os.path.isfile("test.json"))

    c.load()
    assert(len(c) == 1)
    assert(c["Default"] is True)
    assert(not os.path.isfile("test.json"))


def test_accessors(tmp):
    c = ConfigurationFile("test.json")
    assert(len(c) == 0)
    assert(not c.changed)
    c["x"] = "x"
    assert(c.changed)
    assert(len(c) == 1)
    assert(c["x"] == "x")

    del c["x"]
    assert(not c.changed)  # x was added and removed -> no change.
    assert(len(c) == 0)

    with pytest.raises(KeyError):
        print(c["x"])


def test_readonly(tmp):
    c = ConfigurationFile("test.json", {"Default": True}, read_only=True)
    assert(len(c) == 1)
    assert(c["Default"] is True)
    assert(not os.path.isfile("test.json"))

    with pytest.raises(PermissionError):
        c["other"] = "Foo"

    with pytest.raises(PermissionError):
        del c["Default"]

    assert(len(c) == 1)
    assert(list(c) == ["Default"])

    with pytest.raises(io.UnsupportedOperation):
        c.save()


def test_save_default(tmp):
    c = ConfigurationFile("test.json", {"Default": True})
    c.save()
    assert(os.path.isfile("test.json"))

    with open("test.json", 'r') as f:
        data = json.load(f)
        assert(data == {"Default": True})


def test_load_values(tmp):
    with open("test.json", 'w') as f:
        json.dump({"Default": False, "str": "Test string"}, f)

    c = ConfigurationFile("test.json", {"Default": True})
    c.load()
    assert(len(c) == 2)
    assert(c["Default"] is False)
    assert(c["str"] == "Test string")


def test_save_new_value(tmp):
    with open("test.json", 'w') as f:
        json.dump({"Default": False, "str": "Test string"}, f)

    c = ConfigurationFile("test.json", {"Default": True, "This is new": "yes"})
    c.load()
    assert(len(c) == 3)
    assert(c["Default"] is False)
    assert(c["str"] == "Test string")
    assert(c["This is new"] == "yes")

    c.save()
    assert(not c.changed)
    with open("test.json", 'r') as f:
        data = json.load(f)
        assert(data == {"Default": False,
                        "str": "Test string",
                        "This is new": "yes"})


def test_delete_default_value_then_save(tmp):
    c = ConfigurationFile("test.json", {"Default": True})
    assert(not os.path.isfile("test.json"))

    c.load()
    assert(len(c) == 1)
    assert(c["Default"] is True)

    del c["Default"]
    assert(len(c) == 0)

    assert(c.changed)
    c.save()
    assert(not c.changed)
    with open("test.json", 'r') as f:
        data = json.load(f)
        assert(data == {})


def test_delete_nondefault_value_then_save(tmp):
    with open("test.json", 'w') as f:
        json.dump({"Default": False, "str": "Test string"}, f)

    c = ConfigurationFile("test.json", {"Default": True})
    c.load()
    del c["Default"]
    assert(len(c) == 1)
    assert(c["str"] == "Test string")

    c.save()
    with open("test.json", 'r') as f:
        data = json.load(f)
        assert(data == {"str": "Test string"})


def test_context_raises(tmp):
    with ConfigurationFile("test.json", read_only=True) as c:
        with pytest.raises(EnvironmentError):
            c.load()
        with pytest.raises(EnvironmentError):
            c.save()


def test_context_loads(tmp):
    with open("test.json", 'w') as f:
        json.dump({"Default": False, "str": "Test string"}, f)

    with ConfigurationFile("test.json", {"Default": True}, read_only=True) \
            as c:
        assert(c["Default"] is False)
        assert(c["str"] == "Test string")


def test_context_saves(tmp):
    with open("test.json", 'w') as f:
        json.dump({"Default": False, "str": "Test string"}, f)

    with ConfigurationFile("test.json", {"Default": True,
                                         "New Default": 0}) as c:
        assert(c["Default"] is False)
        assert(c["str"] == "Test string")
        assert(c["New Default"] == 0)

        c["str"] = "Foobar"

    with open("test.json", 'r') as f:
        data = json.load(f)
        assert(data == {"Default": False,
                        "New Default": 0,
                        "str": "Foobar"})


def test_context_removes_file_readonly(tmp):
    assert(not os.path.isfile("test.json"))

    with ConfigurationFile("test.json", read_only=True):
        assert(os.path.isfile("test.json"))

    assert(not os.path.isfile("test.json"))


def test_context_doesnt_remove_default_file_non_readonly(tmp):
    assert(not os.path.isfile("test.json"))

    with ConfigurationFile("test.json", {"Default": True}):
        assert(os.path.isfile("test.json"))

    assert(os.path.isfile("test.json"))


def test_nonlocal_file(tmp):
    c = ConfigurationFile(os.path.join("foo", "bar", "cfg.json"))
    c.load()

    c["x"] = 0
    c.save()

    assert(os.path.isdir("foo"))
    assert(os.path.isdir(os.path.join("foo", "bar")))
    assert(os.path.isfile(os.path.join("foo", "bar", "cfg.json")))
