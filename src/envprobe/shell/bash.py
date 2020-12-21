"""
Module for supporting the Bash shell.
"""
from . import register_type
from .bash_like import BashLike


class Bash(BashLike):
    """
    Shell implementation for the Bash shell.
    """
    def __init__(self, pid, config_dir):
        super().__init__(pid, config_dir, "control.sh")

    def get_shell_hook(self):
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

  PROMPT_COMMAND="__envprobe;$PROMPT_COMMAND";
fi
""".format(LOCATION="/dev/null",  # TODO: Fix this!
           CONFIG=self.configuration_directory,
           CONTROL_FILE=self.control_file,
           TYPE=self.shell_type)


register_type('bash', Bash)
