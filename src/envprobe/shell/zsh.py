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


class Zsh(BashLike):
    """Implementation of hooks for the Z Shell.
    Shell implementation for the Zsh shell.
    """
    def __init__(self, pid, config_dir):
        super().__init__(pid, config_dir, "control.zsh")

    def get_shell_hook(self, envprobe_callback_location):
        return """
# If Envprobe isn't registered already.
typeset -ag precmd_functions;
if [[ -z "${{precmd_functions[(r)__envprobe]}}" ]];
then
    export ENVPROBE_CONFIG="{CONFIG}";
    export ENVPROBE_SHELL_PID="{PID}";
    export ENVPROBE_SHELL_TYPE="{TYPE}";

    # Offer the following convenience aliases for the functions below.
    alias ep='envprobe';
    alias epc='envprobe-config';

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

        local CONTROL="";
        envprobe-config consume | IFS= read -rd '' CONTROL;
        eval "$CONTROL";

        return $original_retcode;
    }};

    # The exit hook.
    __envprobe__kill()
    {{
        local hook_text="";
        envprobe-config consume --detach | IFS= read -rd '' hook_text;
        eval "$hook_text";

        # Fire the user's original EXIT-trap we saved when hooking.
        eval "$ENVPROBE_ORIGINAL_EXIT_TRAP";
        unset ENVPROBE_ORIGINAL_EXIT_TRAP;
    }};

    # This is ugly. But unfortunately, in ZSH, if the user has a TRAPEXIT() set
    # then command subsitutions (i.e. "$(foo bar)") would **fire** the
    # TRAPEXIT() when the command returns, causing potential text to be on our
    # output which we then try to eval...
    local trapexit_type="";
    type TRAPEXIT | IFS= read -rd '' trapexit_type;
    if [[ "$trapexit_type" =~ "TRAPEXIT is a shell function" ]];
    then
        # Try the TRAPEXIT function. It is a form of exit hook.
        # "Rename" the exit function to something else, and save it.
        local oldexit="";
        which TRAPEXIT | IFS= read -rd '' oldexit;
        local LINES_ARR=("${{(@f)${{oldexit}}}}");
        shift LINES_ARR;  # Ignore the first line that contains TRAPEXIT word.
        eval "__ep_oldexit() {{ $LINES_ARR";
        export ENVPROBE_ORIGINAL_EXIT_TRAP="__ep_oldexit";

        unset oldexit;
        unset LINES_ARR;
    else
        # Try the normal 'trap' command, and search for an EXIT directive.
        # (The two ways are mutually exclusive.)
        trap | IFS= read -rd '' TRAPS;
        local TRAPS_ARR=("${{(@f)${{TRAPS}}}}");
        for trap_spec in $TRAPS_ARR;
        do
            if [[ "$trap_spec" =~ "EXIT$" ]];
            then
                export ENVPROBE_ORIGINAL_EXIT_TRAP="${{trap_spec//trap -- }}";
                export ENVPROBE_ORIGINAL_EXIT_TRAP="${{ENVPROBE_ORIGINAL_EXIT_TRAP// EXIT}}";  # noqa: E501
            fi;
        done;

        unset TRAPS;
        unset TRAPS_ARR;
        unset trap_spec;
    fi;
    trap __envprobe__kill EXIT;
    unset trapexit_type;

    # Register the hook.
    precmd_functions+=(__envprobe);
fi
""".format(PID=self.shell_pid,
           LOCATION=envprobe_callback_location,
           CONFIG=self.configuration_directory,
           TYPE=self.shell_type)

    def get_shell_unhook(self):
        return """
# If Envprobe has been registered.
if [[ "${{precmd_functions[(r)__envprobe]}}" = "__envprobe" ]];
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
    precmd_functions=(${{precmd_functions:#__envprobe}});
fi
""".format()


register_type('zsh', Zsh)
