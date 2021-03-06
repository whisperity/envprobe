"""
Module for supporting the Bash shell.
"""

from . import register_type
from .bash_like import BashLikeShell


class BashShell(BashLikeShell):
    """
    Shell implementation for the Bash shell.
    """

    def __init__(self):
        super().__init__()

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


register_type('bash', BashShell)
