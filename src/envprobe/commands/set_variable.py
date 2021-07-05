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
from ..library import get_variable_information_manager


name = 'set'
description = \
    """Change the additional information stored for a variable.
    This command allows assigning additional properties, such as an elaborate
    description, to environment variables.

    These settings are stored for your user.
    """
epilog = \
    """TODO: Something about the community descriptions project!
    """
help = "Change the settings (e.g. description) for a variable."


def command(args):
    env_var, _ = args.environment[args.VARIABLE]
    varinfo = env_var.extended_attributes

    conf_to_apply = dict()

    if args.description is not None:
        print("Set description for '{0}'.".format(args.VARIABLE))
        conf_to_apply["description"] = args.description

    if conf_to_apply:
        varinfo.apply(conf_to_apply)

        varinfo_manager = get_variable_information_manager(args.VARIABLE,
                                                           read_only=False)
        # Save the changes with the hardcoded "local" source tag.
        varinfo_manager.set(args.VARIABLE, varinfo, "local")


def register(argparser, shell):
    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help,
            epilog=epilog
    )

    parser.add_argument('VARIABLE',
                        type=str,
                        help="The variable to configure, e.g. PATH.")

    # behavioural = parser.add_argument_group(
    #     "behaviour-affecting arguments",
    #     """Changing these configuration options about a variable alters how
    #     Envprobe behaves when handling the variable.""")

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
