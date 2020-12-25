import pytest

from .helper import bash_shell
from libtest.envprobe import envprobe_location


@pytest.fixture(scope='module')
def sh():
    with bash_shell() as sh:
        yield sh


def test_envprobe_loaded(sh):
    retcode, _ = sh.execute_command("envprobe --help", timeout=1)
    assert(not retcode)

    _, hook_text = sh.execute_command("envprobe config hook bash $$",
                                      timeout=0.5)
    assert("envprobe" in hook_text)
    assert("PROMPT_COMMAND" in hook_text)

    sh.execute_command("""_HOOK=$(cat <<'EOF'
{0}
EOF
)""".format(hook_text))

    retcode, _ = sh.execute_command("eval \"$_HOOK\"", timeout=0.5)
    assert(not retcode)


def test_alias(sh):
    _, result = sh.execute_command("alias")
    assert("alias ep='envprobe'" in result)
    assert("alias epc='envprobe-config'" in result)


def test_get_variable(sh):
    retcode, _ = sh.execute_command("envprobe get", timeout=0.5)
    assert(retcode == 2)

    retcode, result = sh.execute_command("envprobe get PATH",
                                         timeout=0.5)
    assert(not retcode)
    assert(result.startswith("PATH={0}".format(envprobe_location())))

    retcode, result = sh.execute_command("envprobe get ENVPROBE_SHELL_PID",
                                         timeout=0.5)
    assert(retcode == 1)

    retcode, result = sh.execute_command("ep PATH")
    assert(not retcode)
    assert(result.startswith("PATH={0}".format(envprobe_location())))

    retcode, result = sh.execute_command("ep \'?PATH\'")
    assert(not retcode)
    assert(result.startswith("PATH={0}".format(envprobe_location())))


def test_set_variable(sh):
    retcode, _ = sh.execute_command("envprobe set SOMETHING", timeout=0.5)
    assert(retcode == 2)

    _, result = sh.execute_command("echo $DUMMY_VAR $DUMMY_PATH")
    assert(not result)

    retcode, result = sh.execute_command("envprobe set DUMMY_VAR test",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "test")

    retcode, result = sh.execute_command("envprobe set DUMMY_PATH /mnt",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_PATH")
    assert(result == "/mnt")

    retcode, result = sh.execute_command("ep DUMMY_VAR=system", timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "system")

    retcode, result = sh.execute_command("ep \'!DUMMY_VAR\' shortcut",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "shortcut")


def test_undefine_variable(sh):
    retcode, result = sh.execute_command("envprobe undefine NON_EXISTING_VAR",
                                         timeout=0.5)
    assert(not retcode)
    assert(not result)

    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(result == "shortcut")

    retcode, result = sh.execute_command("ep undefine DUMMY_VAR", timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_VAR")
    assert(not result)

    retcode, result = sh.execute_command("ep ^DUMMY_PATH", timeout=0.5)
    assert(not retcode)
    assert(not result)
    _, result = sh.execute_command("echo $DUMMY_PATH")
    assert(not result)
