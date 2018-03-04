"""
Module for supporting the Bash shell.
"""

import os

from . import Shell, register_type


class BashShell(Shell):
    """
    Shell implementation for the Bash shell.
    """

    def __init__(self):
        super().__init__()

    @property
    def shell_pid(self):
        return os.environ.get('ENVPROBE_SHELL_PID', None)

    @property
    def envprobe_location(self):
        location = os.environ.get('ENVPROBE_LOCATION', None)
        if location:
            location = os.path.abspath(os.path.expanduser(location))

        return location

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

  envprobe()
  {{
    _ENVPROBE=1 "{LOCATION}/envprobe.py" "$@";
  }};

  __envprobe()
  {{
    local original_retcode="$?";
    # echo "$(envprobe --help)";
    return $original_retcode;
  }};

  echo "Envprobe loaded successfully. :)";
  PROMPT_COMMAND="__envprobe;$PROMPT_COMMAND";
fi
""".format(PID=pid, LOCATION=location, TYPE=self.shell_type)

    def get_shell_hook_error(self):
        return """
echo "Environment variables for ENVPROBE are missing. Refusing to load..." >&2;
"""


register_type('bash', BashShell)
