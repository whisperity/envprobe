import random

from envprobe import shell


def test_loads_bash(tmp_path):
    environment = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
                   "ENVPROBE_CONFIG": str(tmp_path),
                   "ENVPROBE_SHELL_TYPE": 'bash'
                   }
    sh = shell.get_current_shell(environment)

    assert(sh.shell_type == environment["ENVPROBE_SHELL_TYPE"])
    assert(sh.shell_pid == environment["ENVPROBE_SHELL_PID"])
    assert(sh.configuration_directory == environment["ENVPROBE_CONFIG"])


def test_loads_zsh(tmp_path):
    environment = {"ENVPROBE_SHELL_PID": str(random.randint(1024, 65536)),
                   "ENVPROBE_CONFIG": str(tmp_path),
                   "ENVPROBE_SHELL_TYPE": 'zsh'
                   }
    sh = shell.get_current_shell(environment)

    assert(sh.shell_type == environment["ENVPROBE_SHELL_TYPE"])
    assert(sh.shell_pid == environment["ENVPROBE_SHELL_PID"])
    assert(sh.configuration_directory == environment["ENVPROBE_CONFIG"])
