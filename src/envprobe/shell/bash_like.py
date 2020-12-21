"""
Module for supporting Bash-like shells.
"""
import shlex
import tempfile

from abc import abstractmethod
from .shell import Shell

error_code = \
    "echo \"Environment variables for 'envprobe' are missing. " \
    "Refusing to load...\" >&2;"


class BashLike(Shell):
    """
    Common implementation for Bash-like shells.
    """
    def __init__(self, pid, config_dir, control_filename):
        if not config_dir and pid:
            # Generate a temporary directory that will be used by the shell
            # at every prompt read which *actually* sets the environment as
            # per the user's request. (This is the real "hack" that makes
            # Envprobe usable!)
            tempd = tempfile.mkdtemp(
                prefix='.envprobe.' + self.shell_pid + '-', )
            config_dir = tempd

        super().__init__(pid, config_dir, control_filename)

    @property
    def is_envprobe_capable(self):
        return self.shell_pid

    def get_shell_hook_error(self):
        return error_code

    @property
    def manages_environment_variables(self):
        return True

    def _set_environment_variable(self, env_var):
        with open(self.control_file, 'a') as cfile:
            cfile.write('\n')
            cfile.write("export {0}={1};".format(
                            env_var.name,
                            shlex.quote(env_var.to_raw_var())))

    def _unset_environment_variable(self, env_var):
        with open(self.control_file, 'a') as cfile:
            cfile.write('\n')
            cfile.write("unset {0};".format(env_var.name))
