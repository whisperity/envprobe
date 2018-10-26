# TODO: Refactor the subcommands to a better layout, support dynamic loading.
import os
import sys

from shell import get_current_shell


def get_common_epilogue_or_die():
    epilogue = None
    shell = get_current_shell()

    if len(sys.argv) == 1 or \
            (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        if shell is None:
            epilogue = "You are currently using `envprobe` in a shell that " \
                       "does not have it enabled. Please refer to the "      \
                       "README on how to enable Envprobe."

            if len(sys.argv) == 1:
                print("To see what commands `envprobe` can do, specify "
                      "'--help'.",
                      file=sys.stderr)
        elif shell is False:
            epilogue = "You are currently using an unknown shell, but " \
                       "your environment claims Envprobe is enabled. "  \
                       "Stop hacking your variables! :)"
        else:
            epilogue = "You are currently using a '{0}' shell, and Envprobe " \
                       "is enabled!".format(shell.shell_type)

            if int(os.environ.get('_ENVPROBE', 0)) != 1:
                # If the user is not running the command through an alias,
                # present an error. We don't want users to randomly run
                # envprobe if it is enabled and set up.
                print("You are in an environment where `envprobe` is "
                      "enabled, but you used the command '{0}' to run "
                      "Envprobe, instead of `envprobe`."
                      .format(sys.argv[0]),
                      file=sys.stderr)
                sys.exit(2)

    return epilogue
