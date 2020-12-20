import os
import pytest
import random
import string

from envprobe.environment import VariableDifference, Environment
from envprobe.environment import VariableDifferenceKind as VDK
from envprobe.shell import register_type, shell


class MockVariable:
    def __init__(self, variable, value):
        self.name = variable
        self.value = value

    def to_raw_var(self):
        return self.value


def test_diff_new():
    diff = VariableDifference(VDK.ADDED, "X", None, "Bar",
                              {"diff": [('+', "Bar")]})
    assert(diff.is_simple_change)
    assert(diff.is_new)
    assert(not diff.is_unset)


def test_diff_del():
    diff = VariableDifference(VDK.REMOVED, "X", "Foo", None,
                              {"diff": [('-', "Foo")]})
    assert(diff.is_simple_change)
    assert(not diff.is_new)
    assert(diff.is_unset)


def test_diff_simple():
    diff = VariableDifference(VDK.CHANGED, "X", "Foo", "Bar",
                              {"diff": [('+', "Bar"), ('-', "Foo")]})
    assert(diff.is_simple_change)
    assert(not diff.is_new)
    assert(not diff.is_unset)


def test_diff_not_simple():
    diff = VariableDifference(VDK.CHANGED, "PATH", "/x:/y", "/x:/z",
                              {"diff": [(' ', "/x"),
                                        ('+', "/z"),
                                        ('-', "/y")
                                        ]})
    assert(not diff.is_simple_change)
    assert(not diff.is_new)
    assert(not diff.is_unset)


def _register_mock_shell(rand):
    """
    Create a dummy shell implementation that is injected with the right testing
    parameters but is not visible to the other contexts because it is bound
    to a lambda type inside the function.
    """
    class MockShell(shell.Shell):
        def __init__(self, pid, location, config_dir):
            super().__init__(pid, location, config_dir)

        def is_envprobe_capable(self):
            return True

        def get_shell_hook(self):
            return ""

        def get_shell_hook_error(self):
            return ""

        def _prepare_setting_env_var(self, env_var):
            return "SET %s" % env_var.name

        def _prepare_undefining_env_var(self, env_var):
            return "DEL %s" % env_var.name

    register_type(rand, MockShell)


@pytest.fixture
def mock_shell(scope='module'):
    """
    Generates a randomly named MockShell and registers it as a valid Shell
    implementation under the random name.

    This operation poisons the interpreter with adding a new type into the
    global state, however, due to each such random generation referring a
    unique name with a unique type, there is no possibility for clashes.
    """
    rand_str = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    _register_mock_shell(rand_str)

    yield rand_str

    # Unregister the shell so even a collision on the name won't track back to
    # this test fixture.
    register_type(rand_str, None)


@pytest.fixture
def dummy_shell(mock_shell, tmp_path):
    cfg = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
           "ENVPROBE_CONFIG": str(tmp_path),
           "ENVPROBE_LOCATION": "/dummy",
           "ENVPROBE_SHELL_TYPE": mock_shell}

    env = {"USER": "envprobe",
           "CURRENT_DAY": random.randint(1, 31),
           "INIT_PID": 1,
           "PATH": "/bin:/usr/bin",
           "CMAKE_LIST": "MyModule;FooBar",
           **cfg}

    return shell.get_current_shell(env), env


def test_load_default_state(dummy_shell):
    shell, osenv = dummy_shell
    environment = Environment(shell, osenv)
    assert(environment.current_environment == osenv)
    assert(not environment.stamped_environment)


def test_save_stamps(dummy_shell):
    shell, osenv = dummy_shell
    environment = Environment(shell, osenv)
    environment.save()
    assert(environment.current_environment == osenv)
    assert(environment.stamped_environment == osenv)

    assert(os.path.isfile(shell.state_file))


def test_change(dummy_shell):
    shell, osenv = dummy_shell
    environment = Environment(shell, osenv)
    environment.save()

    with open(shell.state_file, 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(0, 0)
        state_data = f.read(size)

    # Save file is produced. Now we change the environment and load a new one
    # for the *same* shell, simulating Envprobe accessing the same shell's
    # env after a change.
    osenv["USER"] = "root"
    del osenv["INIT_PID"]
    osenv["TEST"] = "test"

    environment = Environment(shell, osenv)
    assert(environment.current_environment != environment.stamped_environment)

    diff = environment.diff()
    add = diff["TEST"]
    assert(add.variable == "TEST" and add.kind == VDK.ADDED)

    rm = diff["INIT_PID"]
    assert(rm.variable == "INIT_PID" and rm.kind == VDK.REMOVED)

    mod = diff["USER"]
    assert(mod.variable == "USER" and mod.kind == VDK.CHANGED)

    environment.save()
    assert(not environment.diff())

    with open(shell.state_file, 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(0, 0)
        state_data_new = f.read(size)

    assert(state_data != state_data_new)


def test_apply_change(dummy_shell):
    shell, osenv = dummy_shell
    environment = Environment(shell, osenv)
    environment.save()
    assert(environment.current_environment == environment.stamped_environment)

    user = MockVariable("USER", "root")
    environment.apply_change(user)
    assert(environment.current_environment != environment.stamped_environment)
    diff = environment.diff()
    # The diff is: USER is "root" in stamped, and "envprobe" in current.
    assert(len(diff) == 1 and "USER" in diff)
    assert(diff["USER"].kind == VDK.CHANGED)

    environment.emit_saved_in_memory()  # stamped -> disk.
    # disk -> current.
    environment = Environment(shell, {**osenv, "USER": "root"})
    assert(environment.current_environment == environment.stamped_environment)

    init_pid = MockVariable("INIT_PID", None)
    environment.apply_change(init_pid, remove=True)
    assert(environment.current_environment != environment.stamped_environment)
    diff = environment.diff()
    # The diff is: INIT_PID is NOT part of stamped, but part of current.
    assert(len(diff) == 1 and "INIT_PID" in diff)
    assert(diff["INIT_PID"].kind == VDK.ADDED)
