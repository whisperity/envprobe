"""
Module for supporting the Bash shell.
"""

import os
import tempfile

from . import Shell, register_type


class BashShell(Shell):
    """
    Shell implementation for the Bash shell.
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

    def get_shell_hook(self):
        pid = self.shell_pid
        location = self.envprobe_location

        # Return a Bash shell script that is loaded by the user's shell.
        # This will call back to envprobe every time the user gets a prompt,
        # letting us execute the environment variable configuration when
        # needed.
        return """
if [[ ! "$PROMPT_COMMAND" =~ "__envprobe" ]];
then
  export ENVPROBE_SHELL_TYPE="{TYPE}";
  export ENVPROBE_CONFIG="{CONFIG}";

  envprobe()
  {{
    _ENVPROBE=1 "{LOCATION}/envprobe.py" "$@";
  }};

  envprobe-config()
  {{
    _ENVPROBE=1 "{LOCATION}/envprobe-config.py" "$@";
  }};

  __envprobe()
  {{
    local original_retcode="$?";
    if [[ -f "{CONTROL_FILE}" ]];
    then
      eval `cat "{CONTROL_FILE}"`;
      rm "{CONTROL_FILE}";
    fi
    return $original_retcode;
  }};

  echo "Envprobe loaded successfully. :)";
  PROMPT_COMMAND="__envprobe;$PROMPT_COMMAND";
fi
""".format(PID=pid,
           LOCATION=location,
           CONFIG=self._configuration_folder,
           CONTROL_FILE=self.control_file,
           TYPE=self.shell_type)

    def get_shell_hook_error(self):
        return """
echo "Environment variables for ENVPROBE are missing. Refusing to load..." >&2;
"""

    def _prepare_setting_env_var(self, env_var):
        return 'export {0}={1};'.format(env_var.name, env_var.to_raw_var())

    def _prepare_undefining_env_var(self, env_var):
        return 'unset {0};'.format(env_var.name)


register_type('bash', BashShell)
