import pytest

from envprobe.environment import Environment
from envprobe.shell import Shell


class MockVar:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def raw(self):
        return self.value


class MockShell(Shell):
    def __init__(self):
        pass

    @property
    def is_envprobe_capable(self):
        return False

    def get_shell_hook(self):
        pass

    @property
    def manages_environment_variables(self):
        return False


@pytest.fixture
def env():
    envp = {"TEST": "Foo"}
    return Environment(MockShell(), envp)


def test_set_variable(env):
    assert(env.current_environment["TEST"] == "Foo")
    assert(not env.stamped_environment)

    var = MockVar("TEST", "Bar")
    env.set_variable(var)

    assert(env.current_environment["TEST"] == "Bar")

    env.stamp()

    assert(env.current_environment["TEST"] == env.stamped_environment["TEST"])

    var.value = "Qux"
    env.set_variable(var, remove=True)

    assert("TEST" not in env.current_environment)
    assert(env.stamped_environment["TEST"] == "Bar")


def test_apply_change(env):
    assert(env.current_environment["TEST"] == "Foo")
    assert(not env.stamped_environment)

    var = MockVar("TEST", "Bar")
    env.apply_change(var)

    assert(env.stamped_environment["TEST"] == "Bar")
    assert(env.current_environment["TEST"] != env.stamped_environment["TEST"])

    var.value = "Qux"
    env.apply_change(var, remove=True)

    assert(env.current_environment["TEST"] == "Foo")
    assert("TEST" not in env.stamped_environment)
