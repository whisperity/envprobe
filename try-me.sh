#!/bin/bash
# Create a temporary HOME directory and run a shell there to test envprobe
# without having to mess up the user's real home.

# -----------------------------------------------------------------------------
# (via http://stackoverflow.com/a/14203146)

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
DO_CLEANUP=0
SHELL="bash"

while getopts "ch?s:" opt; do
    case "$opt" in
    h|\?)
        echo "Usage: try-me.sh [OPTION]..."
        echo
        echo "Start a new shell which has Envprobe enabled, in a *temporary*"
        echo "home directory, to allow trying out Envprobe without anything"
        echo "affecting the current user's configuration."
        echo
        echo -e "\t-c\t\tclean up the temporary HOME after execution"
        echo -e "\t-s SHELL\tuse the given SHELL (defaults to '${SHELL}')"
        echo -e "\t-h\t\tdisplay this help and exit"
        exit 0
        ;;
    c)  DO_CLEANUP=1
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
echo 'eval "$('"$MY_PATH"'/envprobe config hook ${SHELL} $$)"' >> ./.${SHELL}rc
popd

env -u XDG_CONFIG_HOME -u XDG_DATA_HOME -u XDG_RUNTIME_DIR \
    HOME="${TEMPHOME}" TMPDIR="${TEMPHOME}/tmp" \
    ${SHELL}

# Cleanup.
if [ $DO_CLEANUP -eq 1 ]
then
    echo "'-c' was specified, removing temporary HOME..."
    rm -rf "${TEMPHOME}"
fi