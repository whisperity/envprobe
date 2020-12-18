"""
Module for supporting the Bash-like shells.
"""

import os
import tempfile

from abc import abstractmethod
from .shell import Shell


class BashLike(Shell):
    """
    Common implementation for Bash-like shells.
    """

    def __init__(self, pid, location, config_dir):
        super().__init__(pid, location, config_dir)
        if location:
            location = os.path.abspath(os.path.expanduser(location))

        if not config_dir and self.is_envprobe_capable():
            # Generate a temporary file that will be used by the Bash shell
            # at every prompt read which *actually* sets the environment as
            # per the user's request. (This is the real "hack" that makes
            # envprobe useful!)
            tempd = tempfile.mkdtemp(
                prefix='.envprobe.' + self.shell_pid + '-', )
            config_dir = tempd

        super().__init__(pid, location, config_dir)

    def is_envprobe_capable(self):
        return self.shell_pid and self.envprobe_location

    @abstractmethod
    def get_shell_hook(self):
        # Return a shell script that is loaded by the user's shell.
        # This will call back to envprobe every time the user gets a prompt,
        # letting us execute the environment variable configuration when
        # needed.
        return

    def get_shell_hook_error(self):
        return """
echo "Environment variables for ENVPROBE are missing. Refusing to load..." >&2;
"""

    def _prepare_setting_env_var(self, env_var):
        return 'export {0}={1};'.format(env_var.name, env_var.to_raw_var())

    def _prepare_undefining_env_var(self, env_var):
        return 'unset {0};'.format(env_var.name)
