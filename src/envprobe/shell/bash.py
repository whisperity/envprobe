# Copyright (C) 2018 Whisperity
#
# SPDX-License-Identifier: GPL-3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from .bash_like import BashLike
from .core import register_type


class Bash(BashLike):
    """Implementation of hooks for the Bourne Again Shell.
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
        echo "[Debug] Executing Envprobe Bash hook..." >&2;
        if [[ -f "{CONTROL_FILE}" ]]; then
            source "{CONTROL_FILE}";
            cat "{CONTROL_FILE}" >&2; echo >&2;
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
