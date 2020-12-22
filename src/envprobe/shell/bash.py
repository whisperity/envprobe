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

    def get_shell_hook(self, envprobe_callback_location):
        return """
# If Envprobe isn't registered already.
if [[ ! "$PROMPT_COMMAND" =~ "__envprobe" ]];
then
    # Set up the internal variables needed in the env.
    export ENVPROBE_CONFIG="{CONFIG}";
    export ENVPROBE_SHELL_PID={PID};
    export ENVPROBE_SHELL_TYPE="{TYPE}";

    # Offer the following convenience aliases for the functions below.
    alias ep="envprobe";
    alias epc="envprobe-config";

    envprobe()
    {{
      _ENVPROBE=1 PYTHONPATH="{LOCATION}" \
        python3 -m envprobe \
          main "$@";
    }};

    envprobe-config()
    {{
      _ENVPROBE=1 PYTHONPATH="{LOCATION}" \
        python3 -m envprobe \
          config "$@";
    }};

    # The prompt hook.
    __envprobe()
    {{
      local original_retcode="$?";
      if [[ -f "{CONTROL_FILE}" ]]; then
          source "{CONTROL_FILE}";
          rm "{CONTROL_FILE}";
      fi;
      return $original_retcode;
    }};

    # Register the hook.
    echo "Envprobe loaded successfully. :)";
    PROMPT_COMMAND="__envprobe;$PROMPT_COMMAND";
fi
""".format(PID=self.shell_pid,
           LOCATION=envprobe_callback_location,
           CONFIG=self.configuration_directory,
           CONTROL_FILE=self.control_file,
           TYPE=self.shell_type)


register_type('bash', Bash)
