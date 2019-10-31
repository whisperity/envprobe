"""
Module for supporting the Bash-like shells.
"""

import os
import tempfile

from abc import abstractmethod
from . import Shell


class BashLikeShell(Shell):
    """
    Common implementation for Bash-like shells.
    """

    def __init__(self):
        super().__init__()
        self._shell_pid = os.environ.get('ENVPROBE_SHELL_PID', None)

        location = os.environ.get('ENVPROBE_LOCATION', None)
        if location:
            location = os.path.abspath(os.path.expanduser(location))
        self._envprobe_location = location

        self._configuration_folder = os.environ.get('ENVPROBE_CONFIG', None)
        if not self._configuration_folder and self.is_envprobe_capable():
            # Generate a temporary file that will be used by the Bash shell
            # at every prompt read which *actually* sets the environment as
            # per the user's request. (This is the real "hack" that makes
            # envprobe useful!)
            tempd = tempfile.mkdtemp(
                prefix='.envprobe.' + self.shell_pid + '-', )
            self._configuration_folder = tempd

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
