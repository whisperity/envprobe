"""
Main entry point for the Envprobe tool. This module handles the parsing of
command-line arguments and dispatching the user's request to the submodules.
"""
import argparse
import sys

from commands import get_common_epilogue_or_die


def __main():
    """
    Entry point.
    """
    epilogue = get_common_epilogue_or_die()
    parser = argparse.ArgumentParser(
        prog='envprobe',
        description="Envprobe helps you set up your shell environment "
                    "variables in an easy way, with no need of creating and "
                    "editing configuration files and loading them manually.",
        epilog=epilogue
    )

    args = parser.parse_args(sys.argv[1:])  # Cut the shell command's name.
    if 'func' in args:
        try:
            args.func(args)
        except Exception as e:
            print("Cannot execute the specified action.")
            print(str(e))
            import traceback
            traceback.print_exc()
    else:
        print(epilogue)


# Define an entry point so that the tool is usable by calling "./envprobe.py".
if __name__ == "__main__":
    __main()
