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
from envprobe.shell.bash_like import BashLike
from envprobe.shell.core import register_type


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
        python3 "{LOCATION}/envprobe" \
            main "$@";
    }};

    envprobe-config()
    {{
        python3 "{LOCATION}/envprobe" \
            config "$@";
    }};

    # The prompt hook.
    __envprobe()
    {{
        local original_retcode="$?";

        local CONTROL="$(envprobe-config consume)";
        eval "$CONTROL";

        return $original_retcode;
    }};

    # The exit hook.
    __envprobe__kill()
    {{
        eval "$(envprobe-config consume --detach)";

        # Fire the user's original EXIT-trap we saved when hooking.
        eval "$ENVPROBE_ORIGINAL_EXIT_TRAP";
        unset ENVPROBE_ORIGINAL_EXIT_TRAP;
    }};

    export ENVPROBE_ORIGINAL_EXIT_TRAP="$(trap -p EXIT)";
    if [[ ! -z "$ENVPROBE_ORIGINAL_EXIT_TRAP" ]];
    then
        # Store the original trap command's configuration, if any.
        export ENVPROBE_ORIGINAL_EXIT_TRAP="${{ENVPROBE_ORIGINAL_EXIT_TRAP//trap -- \\'/}}";  # noqa: E501
        export ENVPROBE_ORIGINAL_EXIT_TRAP="${{ENVPROBE_ORIGINAL_EXIT_TRAP//\\' EXIT/}}";     # noqa: E501
    fi;
    trap __envprobe__kill EXIT;

    # Register the hook.
    PROMPT_COMMAND="__envprobe;$PROMPT_COMMAND";
fi
""".format(PID=self.shell_pid,
           LOCATION=envprobe_callback_location,
           CONFIG=self.configuration_directory,
           TYPE=self.shell_type)

    def get_shell_unhook(self):
        return """
# If Envprobe has been registered.
if [[ "$PROMPT_COMMAND" =~ "__envprobe" ]];
then
    # Unset the internal variables.
    unset ENVPROBE_CONFIG;
    unset ENVPROBE_SHELL_PID;
    unset ENVPROBE_SHELL_TYPE;

    # Destroy the convenience aliases.
    unalias ep;
    unalias epc;

    unset -f envprobe;
    unset -f envprobe-config;

    # The prompt hook and the exit hook.
    unset -f __envprobe;
    unset -f __envprobe__kill;

    # Unregister the prompt hook.
    PROMPT_COMMAND=${{PROMPT_COMMAND//__envprobe;/}}
fi
""".format()


register_type('bash', Bash)
