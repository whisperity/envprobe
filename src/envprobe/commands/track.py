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
from enum import Enum
import os

from envprobe.settings import get_configuration_directory
from envprobe.settings.config_file import ConfigurationFile
from envprobe.settings.variable_tracking import \
    get_tracking_file_name, VariableTracking


name = 'track'
description = \
    """Configure an environment variable's \"tracking status\".

    A tracked variable's value changes are reflected in Envprobe's saved
    environment snapshots. If a variable is ignored, Envprobe can still be
    used to query or change the value, but the changes are not saved to
    snapshots."""
help = "Configure the tracking status of variables."
epilogue = \
    """
    The trackedness of a variable is resolved in the following way.

    Local explicit tracking or ignored status (as set by '--local' and
    '--track'/'--ignore') take first priority.

    If the variable is not configured locally, but is explicitly configured
    globally ('--global'), the global configuration decides.

    If neither local nor global explicit settings exists for the variable,
    the '--default' tracking behaviour for the local session, and then for
    the global configuration is queried.

    If none of the previous provide an answer, the variable will be deemed
    tracked.
    """

scopeargs_description_common = \
    """Environment variable tracking is configured on two levels: the current
    shell's level (\"local\") and the user's level (\"global\"). Shell-specific
    configurations do not apply in other shells running Envprobe.
    """

scopeargs_description_local_and_global = scopeargs_description_common + \
    """
    By default, the 'track' command changes the local configuration.
    """

scopeargs_description_global_only = scopeargs_description_common + \
    """
    Envprobe is not installed properly to run in the current shell, and as
    such, only the \"global\" configuration can be modified.
    """


class Scope(Enum):
    LOCAL = 0
    GLOBAL = 1


class Mode(Enum):
    QUERY = 0
    TRACK = 1
    IGNORE = 2
    RESET = 3


def _handle_default(tracker, args):
    if args.default is not True:
        raise AttributeError("default == True required for handle_default.")

    if args.setting == Mode.QUERY:
        if args.scope == Scope.GLOBAL:
            print("global default: {0}"
                  .format("track" if tracker.global_tracking
                          else "ignore"))
        elif args.scope == Scope.LOCAL:
            print("local default: {0}"
                  .format("not configured"
                          if tracker.local_tracking is None else
                          "ignore" if not tracker.local_tracking else
                          "track"))
        return

    if args.scope == Scope.GLOBAL:
        if args.setting == Mode.TRACK:
            tracker.global_tracking = True
        elif args.setting == Mode.IGNORE:
            tracker.global_tracking = False
        elif args.setting == Mode.RESET:
            raise AttributeError("'--reset' for global default invalid.")
    elif args.scope == Scope.LOCAL:
        if args.setting == Mode.TRACK:
            tracker.local_tracking = True
        elif args.setting == Mode.IGNORE:
            tracker.local_tracking = False
        elif args.setting == Mode.RESET:
            tracker.local_tracking = None


def _handle_querying_variable(tracker, args):
    if args.setting != Mode.QUERY:
        raise AttributeError("--query required for handle_querying_variable.")

    print("{0}: {1}"
          .format(args.VARIABLE,
                  "tracked" if tracker.is_tracked(args.VARIABLE)
                  else "ignored"))
    if tracker.is_explicitly_configured_local(args.VARIABLE):
        print("\tlocal explicit {0}"
              .format("TRACK" if tracker.is_tracked_local(args.VARIABLE)
                      else "IGNORE"))
    if tracker.is_explicitly_configured_global(args.VARIABLE):
        print("\tglobal explicit {0}"
              .format("TRACK" if tracker.is_tracked_global(args.VARIABLE)
                      else "IGNORE"))


def _handle_setting_variable(tracker, args):
    # Execute the setting of the variable through the tracker.
    function_prefix = {Mode.TRACK: "track",
                       Mode.IGNORE: "ignore",
                       Mode.RESET: "unset"}[args.setting]
    function_suffix = {Scope.GLOBAL: "global",
                       Scope.LOCAL: "local"}[args.scope]
    function_to_call = "{0}_{1}".format(function_prefix, function_suffix)
    func = getattr(tracker, function_to_call, None)
    if not callable(func):
        raise AttributeError("No function '{0}' on the tracker backend!"
                             .format(function_to_call))
    return func(args.VARIABLE)


def command(args):
    # Create our own tracking instance here because this command might write
    # the configuration file.
    is_write_action = args.setting in [Mode.TRACK, Mode.IGNORE, Mode.RESET]
    if args.shell.is_envprobe_capable:
        local_config_file = ConfigurationFile(
            os.path.join(args.shell.configuration_directory,
                         get_tracking_file_name()),
            VariableTracking.config_schema_local,
            read_only=args.scope != Scope.LOCAL or
            (args.scope == Scope.LOCAL and not is_write_action)
        )
    else:
        local_config_file = None
    global_config_file = ConfigurationFile(
        os.path.join(get_configuration_directory(), get_tracking_file_name()),
        VariableTracking.config_schema_global,
        read_only=args.scope != Scope.GLOBAL or (args.scope == Scope.GLOBAL and
                                                 not is_write_action)
    )
    tracker = VariableTracking(global_config_file, local_config_file)

    if args.default:
        return _handle_default(tracker, args)

    if args.setting == Mode.QUERY:
        return _handle_querying_variable(tracker, args)

    return _handle_setting_variable(tracker, args)


def register(argparser, shell):
    manage_local_config = shell.is_envprobe_capable \
        and shell.manages_environment_variables

    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help,
            epilog=epilogue
    )

    target = parser.add_argument_group() \
        .add_mutually_exclusive_group(required=True)
    target.add_argument('VARIABLE',
                        type=str,
                        nargs='?',  # Make the name optional.
                        help="The name of the environment variable which "
                             "the tracking status is configured for, e.g. "
                             "EDITOR or PATH.")
    target.add_argument('-d', '--default',
                        action='store_true',
                        help="Configure the default behaviour instead of the "
                             "status of one environment variable.")

    setting = parser.add_argument_group("mode arguments") \
        .add_mutually_exclusive_group()
    setting.add_argument('-t', '--track',
                         dest='setting',
                         action='store_const',
                         const=Mode.TRACK,
                         help="Set the variable to be explicitly tracked, "
                              "overriding the defaults. If the '--default' "
                              "option is used, set the default for all "
                              "variables to be tracked without an explicit "
                              "ignore set.")
    setting.add_argument('-i', '--ignore', '--no-track',
                         dest='setting',
                         action='store_const',
                         const=Mode.IGNORE,
                         help="Set the variable to be explicitly ignored, "
                              "overriding the defaults. If the '--default' "
                              "option is used, set the default for all "
                              "variables to be ignored without an explicit "
                              "track set.")
    setting.add_argument('-r', '--reset',
                         dest='setting',
                         action='store_const',
                         const=Mode.RESET,
                         help="Delete the explicit setting for the variable's "
                              "tracking configuration, and make it use the "
                              "default instead. This option cannot be used "
                              "if the '--global' and '--default' options are "
                              "given.")
    setting.add_argument('-q', '--query',
                         dest='setting',
                         action='store_const',
                         const=Mode.QUERY,
                         help="Query the tracking status of the variable, or "
                              "the default tracking setting. If a VARIABLE is "
                              "given, this command ignores the scope "
                              "arguments and produces a detailed output using "
                              "all available configuration files.")

    scope = parser.add_argument_group(
        "scope arguments",
        description=scopeargs_description_local_and_global
        if manage_local_config
        else scopeargs_description_global_only).add_mutually_exclusive_group()
    if manage_local_config:
        scope.add_argument('-l', '--local',
                           dest='scope',
                           action='store_const',
                           const=Scope.LOCAL,
                           help="Get or set the configuration for the current "
                                "shell session. Changes made will not be "
                                "available in other shells.")
    scope.add_argument('-g', "--global",
                       dest='scope',
                       action='store_const',
                       const=Scope.GLOBAL,
                       help="Get or set the configuration for your user. "
                            "Changes are persisted in configuration files and "
                            "are visible in and affecting all Envprobe "
                            "operations.")
    parser.set_defaults(scope=Scope.LOCAL if manage_local_config
                        else Scope.GLOBAL)
    parser.set_defaults(setting=Mode.QUERY)

    def _sanitise_input(args):
        if args.scope == Scope.GLOBAL and args.setting == Mode.RESET and \
                args.default:
            parser.error("argument -r/--reset is not allowed if -g/--global "
                         "and -d/--default are both specified.")

        return command(args)

    parser.set_defaults(func=_sanitise_input)
