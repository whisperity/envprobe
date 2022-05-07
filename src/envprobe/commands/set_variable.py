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
from envprobe.environment import create_environment_variable
from envprobe.library import get_variable_information_manager
from envprobe import vartypes

name = 'set'
description = \
    """Change the additional information stored for a variable.
    This command allows assigning additional properties, such as an elaborate
    description, to environment variables.

    These settings are stored for your user.
    """
epilog = \
    """The meaning of potential options for the '--type' flag are:

    {0}

    If you believe the new settings of the variable is useful for others,
    please submit us an issue on the "variable descriptions" project at
    http://github.com/whisperity/Envprobe-Descriptions
    """
help = "Change the settings (e.g. type, or description) for a variable."


def command(args):
    try:
        env_var, _ = args.environment[args.VARIABLE]
    except Exception:
        # The environment variable object failed to instantiate. This commonly
        # happens if the type conflicts with the value in the environment.
        # To allow the user to continue, we can always fall back using the
        # default heuristics.
        env_var = create_environment_variable(
            args.VARIABLE, args.environment.current_environment)
    varinfo = env_var.extended_attributes

    conf_to_apply = dict()

    if args.type is not None:
        print("Set type for '{0}'.".format(args.VARIABLE))
        conf_to_apply["type"] = args.type

    if args.description is not None:
        print("Set description for '{0}'.".format(args.VARIABLE))
        conf_to_apply["description"] = args.description

    if conf_to_apply:
        varinfo.apply(conf_to_apply)

        varinfo_manager = get_variable_information_manager(args.VARIABLE,
                                                           read_only=False)
        if all(not x for x in conf_to_apply.values()):
            # If all the configuration is gone (reset to empty) for the
            # variable, delete the entire record.
            del varinfo_manager[args.VARIABLE]
        else:
            # Save the changes with the hardcoded "local" source tag.
            varinfo_manager.set(args.VARIABLE, varinfo, "local")


def register(argparser, shell):
    # To generate a proper help and list of valid choices for the --type flag,
    # we need to eagerly load the full implementation.
    vartypes.load_all()
    vartype_description_in_epilogue = ""
    for vartype in sorted(vartypes.get_known_kinds()):
        vartype_description_in_epilogue += "{0}: {1} ".format(
            vartype.upper(), vartypes.get_class(vartype).type_description())
    fmt_epilog = epilog.format(vartype_description_in_epilogue)
    # TODO: Ignored/disabled type which prohibits access to it completely.

    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help,
            epilog=fmt_epilog
    )

    parser.add_argument('VARIABLE',
                        type=str,
                        help="The variable to configure, e.g. PATH.")

    behavioural = parser.add_argument_group(
        "behaviour-affecting arguments",
        """Changing these configuration options about a variable alters how
        Envprobe behaves when handling the variable.""")

    behavioural.add_argument('-t', '--type',
                             type=str,
                             choices=[''] + sorted(vartypes.get_known_kinds()),
                             help="Change the type of the variable from "
                                  "Envprobe's point of view to the specified "
                                  "version. This affects how you interact "
                                  "with the variable in the future! To "
                                  "disregard additional behaviour, set the "
                                  "type to 'string'. Set to empty string "
                                  "(\"\") to delete the stored configuration "
                                  "and return to defaults. For details on "
                                  "what each option means, see the end of "
                                  "the command's help.")

    informational = parser.add_argument_group(
        "informational arguments",
        """These configuration options attach additional information to the
        variable which can be queried later, but do not affect behaviour.""")

    informational.add_argument('--description',
                               type=str,
                               help="Change the long, human-readable "
                                    "description of the variable to the "
                                    "given text. Set to empty string (\"\") "
                                    "to delete the stored description. The "
                                    "description is printed when full "
                                    "information is requested about the "
                                    "variable.")

    parser.set_defaults(func=command)
