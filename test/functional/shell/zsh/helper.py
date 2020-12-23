from contextlib import contextmanager
import os
import sys

from libtest.envprobe import envprobe_location
from libtest.shell import Shell


@contextmanager
def zsh_shell():
    """
    This function provides a spawned Zsh shell where Envprobe is available.
    """
    envprobe_at = envprobe_location()

    with Shell("zsh", "--no-rcs --no-promptsp --interactive --shinstdin",
               "echo $?", ";\n") as shell:
        _, pid = shell.execute_command("echo $$")
        print("[Zsh] Spawned {0}".format(pid), file=sys.stderr)

        # Make sure envprobe is not available initially.
        retcode, value = shell.execute_command("which envprobe")
        assert(retcode == 1)

        print("[Zsh] Adding '{0}' to PATH...".format(envprobe_at),
              file=sys.stderr)
        shell.execute_command("export PATH=\"{0}:$PATH\"".format(envprobe_at))

        retcode, value = shell.execute_command("which envprobe")
        print("[Zsh] Resolved 'envprobe' to be at '{0}'".format(value),
              file=sys.stderr)
        assert(retcode == 0)
        assert(os.path.dirname(value) == envprobe_at)

        yield shell
