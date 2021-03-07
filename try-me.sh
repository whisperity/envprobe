#!/bin/bash

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
# Create a temporary HOME directory and run a shell there to test envprobe
# without having to mess up the user's real home.


# -----------------------------------------------------------------------------
# (via http://stackoverflow.com/a/14203146)

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
LOAD_ENVPROBE=1
KEEP_TEMPORARY_HOME=0
SHELL="bash"

while getopts "hkn?s:" opt; do
    case "$opt" in
    h|\?)
        echo "Usage: try-me.sh [OPTION]..."
        echo
        echo "Start a new shell which has Envprobe enabled, in a *temporary*"
        echo "home directory, to allow trying out Envprobe without anything"
        echo "affecting the current user's configuration."
        echo
        echo -e "\t-k\t\tdo not clean up the temporary HOME after execution"
        echo -e "\t-n\t\tdry-run: start a shell, but do NOT load 'Envprobe'"
        echo -e "\t-s SHELL\tuse the given SHELL (defaults to '${SHELL}')"
        echo -e "\t-h\t\tdisplay this help and exit"
        exit 0
        ;;
    k)  KEEP_TEMPORARY_HOME=1
        ;;
    n)  LOAD_ENVPROBE=0
        ;;
    s)  SHELL="${OPTARG}"
        ;;
    esac
done

shift $((OPTIND-1))

[ "${1:-}" = "--" ] && shift


# ----------------------------------------------------------------------------
# (via http://stackoverflow.com/a/630387)

MY_PATH="`dirname \"$0\"`"              # relative
MY_PATH="`( cd \"$MY_PATH\" && pwd )`"  # absolutized and normalized
if [ -z "$MY_PATH" ] ; then
  # error; for some reason, the path is not accessible
  # to the script (e.g. permissions re-evaled after suid)
  exit 1  # fail
fi


# ----------------------------------------------------------------------------

TEMPHOME=$(mktemp --directory -p "$MY_PATH" ".testhome-XXXXXX")

pushd ${TEMPHOME}
touch \
    .${SHELL}rc \
    .is_temporary_home \
    .sudo_as_admin_successful
mkdir tmp
if [ $LOAD_ENVPROBE -eq 1 ]
then
    echo 'eval "$('"$MY_PATH"'/envprobe config hook ${SHELL} $$)"' \
        >> ./.${SHELL}rc
fi
popd

env -u XDG_CONFIG_HOME -u XDG_DATA_HOME -u XDG_RUNTIME_DIR \
    -u ENVPROBE_SHELL_PID -u ENVPROBE_SHELL_TYPE -u ENVPROBE_CONFIG \
    HOME="${TEMPHOME}" TMPDIR="${TEMPHOME}/tmp" \
    ${SHELL}

# Cleanup.
if [ $KEEP_TEMPORARY_HOME -ne 1 ]
then
    rm -rf "${TEMPHOME}"
fi
