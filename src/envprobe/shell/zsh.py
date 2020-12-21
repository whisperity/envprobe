"""
Module for supporting the Zsh shell.
"""
from . import register_type
from .bash_like import BashLike


class Zsh(BashLike):
    """
    Shell implementation for the Zsh shell.
    """
    def __init__(self, pid, config_dir):
        super().__init__(pid, config_dir, "control.zsh")

    def get_shell_hook(self):
        return """
if [[ "${{precmd_functions[(r)__envprobe]}}" = "" ]];
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

  precmd_functions+=(__envprobe);
fi
""".format(LOCATION="/dev/null",  # TODO: Fix this!
           CONFIG=self.configuration_directory,
           CONTROL_FILE=self.control_file,
           TYPE=self.shell_type)


register_type('zsh', Zsh)
