"""
Module for supporting Bash-like shells.
"""
import shlex

from .core import Shell


class BashLike(Shell):
    """Common implementation for Bash-like shells.
    """
    def __init__(self, pid, config_dir, control_filename):
        super().__init__(pid, config_dir, control_filename)

    @property
    def is_envprobe_capable(self):
        return self.shell_pid

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
