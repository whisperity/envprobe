import pytest

from .helper import zsh_shell
from libtest.envprobe import envprobe_location


@pytest.fixture(scope='module')
def sh():
    with zsh_shell() as sh:
        yield sh


def test_envprobe_loaded(sh):
    retcode, _ = sh.execute_command("envprobe --help", timeout=1)
    assert(not retcode)

    _, hook_text = sh.execute_command("envprobe config hook zsh $$",
                                      timeout=0.5)
    assert("envprobe" in hook_text)
    assert("precmd_functions" in hook_text)

    sh.execute_command("""_HOOK=$(cat <<'EOF'
{0}
EOF
)""".format(hook_text))

    retcode, _ = sh.execute_command("eval \"$_HOOK\"", timeout=0.5)
    assert(not retcode)


def test_alias(sh):
    _, result = sh.execute_command("alias")
    assert("ep=envprobe" in result)
    assert("epc=envprobe-config" in result)


def test_get_variable(sh):
    retcode, result = sh.execute_command("envprobe get PATH")
    assert(not retcode)
    assert(result.startswith("PATH={0}".format(envprobe_location())))

    retcode, result = sh.execute_command("envprobe get ENVPROBE_SHELL_PID")
    assert(retcode == 1)
