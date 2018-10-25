"""
Handles user-facing operations related to tweaking the tracking status of
variables.
"""
from configuration import global_config
from configuration.tracked_variables import TrackingOverlay
from shell import get_current_shell


def __track(args):
    tracking = TrackingOverlay(get_current_shell())
    if args.ignore:
        tracking.ignore(args.VARIABLE, args.global_scope)
    elif args.default:
        tracking.make_default(args.VARIABLE, args.global_scope)
    else:
        tracking.track(args.VARIABLE, args.global_scope)
    tracking.flush(args.global_scope)


def __change_default(args):
    tracking = TrackingOverlay(get_current_shell())
    tracking.set_default(args.track, args.global_scope)
    tracking.flush(args.global_scope)


def __create_track_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='track',
        description="Change a variable's tracking status. A tracked "
                    "variable's value changes is reflected in Envprobe "
                    "saves.",
        help="Change a variable's tracking status."
    )

    parser.add_argument(
        'VARIABLE',
        type=str,
        help="The variable which is to be tracked, e.g. PATH."
    )

    if get_current_shell():
        # Only allow the changing the non-global configuration if there
        # is a shell that is loaded.
        parser.add_argument('-g', '--global',
                            dest='global_scope',
                            action='store_true',
                            help="Save the tracking status into your user "
                                 "configuration, not to the settings of the "
                                 "current Shell.")

    mgroup = parser.add_argument_group('additional tracking settings')
    mgroup = mgroup.add_mutually_exclusive_group()

    mgroup.add_argument('-i', '--ignore',
                        action='store_true',
                        help="Set the variable to be ignored instead of "
                             "tracked. An ignored variable's value changes "
                             "are not reflected in Envprove saves.")

    mgroup.add_argument('-d', '--default',
                        action='store_true',
                        help="Remove both the track and ignore status of "
                             "VARIABLE. After this, the user's or shell's "
                             "(depending on whether '-g' was specified) "
                             "default tracking behaviour will be "
                             "applicable.")

    parser.set_defaults(func=__track)
    if not get_current_shell():
        # If a shell could not be loaded, default to changing the global
        # state.
        parser.set_defaults(global_scope=True)
    global_config.REGISTERED_COMMANDS.append('track')


def __create_default_tracking_subcommand(main_parser):
    parser = main_parser.add_parser(
        name='default-tracking',
        description="Change the default tracking behaviour of variables.",
        help="Change the default tracking behaviour of variables."
    )

    ngroup = parser.add_mutually_exclusive_group(required=True)

    ngroup.add_argument('-t', '--track', '-e', '--enable',
                        dest='track',
                        action='store_true',
                        help="Set the default behaviour to track all "
                             "(not explicitly ignored) variables.")

    ngroup.add_argument('-i', '--ignore', '-d', '--disable',
                        dest='ignore',
                        action='store_true',
                        help="Set the default behaviour to ignore all "
                             "(not explicitly tracked) variables.")

    if get_current_shell():
        # Only allow the changing the non-global configuration if there
        # is a shell that is loaded.
        parser.add_argument('-g', '--global',
                            dest='global_scope',
                            action='store_true',
                            help="Save the tracking status into your user "
                                 "configuration, not to the settings of the "
                                 "current Shell.")

    parser.set_defaults(func=__change_default)
    if not get_current_shell():
        # If a shell could not be loaded, default to changing the global
        # state.
        parser.set_defaults(global_scope=True)
    global_config.REGISTERED_COMMANDS.append('default-tracking')


def create_subcommand_parser(main_parser):
    # Only expose these commands of this module if the user is running
    # envprobe in a known valid shell.
    __create_track_subcommand(main_parser)
    __create_default_tracking_subcommand(main_parser)
