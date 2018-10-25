"""
Handles the operations related to the saving and loading the user's saved
environments.
"""

from configuration import global_config
from shell import get_current_shell
from state import environment


def __diff(args):
    TYPES = environment.VariableDifferenceType

    env = environment.Environment(get_current_shell())
    diffs = env.diff()

    for variable_name in sorted(list(diffs.keys())):
        if args.variable and variable_name not in args.variable:
            continue

        diff = diffs[variable_name].differences
        if args.type == 'normal':
            kind = diffs[variable_name].type
            if kind == TYPES.ADDED:
                kind = 'Added:'
            elif kind == TYPES.REMOVED:
                kind = 'Removed:'
            elif kind == TYPES.CHANGED:
                kind = 'Modified:'

            print("%s %s" % (kind.ljust(9), variable_name))
            if len(diff) == 1:
                # If only a remove or an addition took place, show the new
                # value.
                print("   value: %s" % diff[0][1])
            elif len(diff) == 2 and \
                    diff[0][0] == '+' and diff[1][0] == '-':
                # If the difference is exactly a single change from a value
                # to another, just show the change.
                print("    from: %s\n      to: %s" % (diff[0][1], diff[1][1]))
            else:
                for action, value in diff:
                    if action == ' ':
                        # Do not show "keep" or "unchanged" lines.
                        continue
                    elif action == '+':
                        print("    added %s" % value)
                    elif action == '-':
                        print("  removed %s" % value)

            print()
        elif args.type == 'unified':
            old_name, new_name = variable_name, variable_name
            old_start, old_count, new_start, new_count = \
                1, len(diff), 1, len(diff)

            if diffs[variable_name].type == TYPES.ADDED:
                old_name = '(new variable)'
                old_start, old_count = 0, 0
            elif diffs[variable_name].type == TYPES.REMOVED:
                new_name = '(variable unset)'
                new_start, new_count = 0, 0

            print("--- %s" % old_name)
            print("+++ %s" % new_name)
            print("@@ -%d,%d +%d,%d @@"
                  % (old_start, old_count, new_start, new_count))
            for difference in diff:
                print("%s %s" % difference)
            print()


def __create_diff_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='diff',
        description="Shows the difference between the previously "
                    "saved/loaded state and the current environment of the "
                    "shell.",
        help="Show difference of shell vs. previous save/load."
    )

    parser.add_argument('variable',
                        metavar='VARIABLE',
                        nargs='*',
                        help="Show only the difference for the specified "
                             "variables. If a variable has no difference, "
                             "it is ignored.")

    format = parser.add_argument_group("formatting arguments")
    format = format.add_mutually_exclusive_group()

    format.add_argument('-n', '--normal',
                        dest='type',
                        action='store_const',
                        const='normal',
                        help="Show a \"normal\", human-readable difference.")

    format.add_argument('-u', '--unified',
                        dest='type',
                        action='store_const',
                        const='unified',
                        help="Show a unified diff (like calling `diff -u`) "
                             "which can be machine-read.")

    parser.set_defaults(func=__diff,
                        type="normal")
    global_config.REGISTERED_COMMANDS.append('diff')


def create_subcommand_parser(main_parser):
    if not get_current_shell():
        return

    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_diff_subcommand(main_parser)
