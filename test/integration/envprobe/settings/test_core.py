from copy import deepcopy
import os
import pytest
import tempfile

from envprobe.settings.core import get_configuration_directory, \
        get_data_directory, get_runtime_directory


@pytest.fixture
def noenv():
    env = deepcopy(os.environ)
    try:
        del os.environ["XDG_CONFIG_HOME"]
    except KeyError:
        pass

    try:
        del os.environ["XDG_DATA_HOME"]
    except KeyError:
        pass

    try:
        del os.environ["XDG_RUNTIME_DIR"]
    except KeyError:
        pass

    yield

    os.environ = env


@pytest.fixture
def xdg():
    env = deepcopy(os.environ)
    os.environ["XDG_CONFIG_HOME"] = "/var/user_data/cfg"
    os.environ["XDG_DATA_HOME"] = "/var/user_data"
    os.environ["XDG_RUNTIME_DIR"] = "/run/ep1"

    yield

    os.environ = env


def test_dir(noenv):
    assert(get_configuration_directory() ==
           os.path.join(os.path.expanduser('~'), ".config", "envprobe"))
    assert(get_data_directory() ==
           os.path.join(os.path.expanduser('~'),
                        ".local", "share", "envprobe"))
    assert(get_runtime_directory("X") ==
           os.path.join(tempfile.gettempdir(), "envprobe-X"))


def test_dir_with_env(xdg):
    assert(get_configuration_directory() ==
           os.path.join("/var/user_data/cfg", "envprobe"))
    assert(get_data_directory() ==
           os.path.join("/var/user_data", "envprobe"))
    assert(get_runtime_directory(None) ==
           os.path.join("/run/ep1", "envprobe"))
