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
import sys
import tempfile

from envprobe.community_descriptions import downloader, local_data
from envprobe.vartypes import EnvVarExtendedInformation


name = 'descriptions'
description = \
    """
    The 'descriptions' subcommand allows access to the "Envprobe Variable
    Descriptions Knowledge Base" project.
    """
help = "Access facilities related to the \"variable desciptions\" project"

update_name = 'update'
update_description = \
    """
    Check if the descriptions project has a newer version available.
    If there is, the data will be downloaded and extracted and subsequent calls
    to Envprobe will behave according to the new information, if no
    user-specific settings exist.

    This command requires Internet access.
    """
update_help = "Download varaible descriptions from the Internet."

epilogue = \
    """
    The canonical repository for this sister project is avaiable at:
    http://github.com/whisperity/Envprobe-Descriptions
    """


def update_command(args):
    print("Checking for latest version of the Envprobe Variable Descriptions "
          "Knowledge Base project.")
    storage_cfg = local_data.get_storage_configuration(read_only=False)
    new_version = downloader.fetch_latest_version_information()

    if new_version == storage_cfg.version:
        # Right now, we use a simple equality check, because the versions are
        # pure commit IDs.
        print("Nothing to update - the latest data is already available.")
        return

    # Open all the variable information managers for the saved data. This is
    # needed so we can gather which keys to delete.
    variables_to_clear = set()
    for manager in local_data.generate_variable_information_managers():
        variables_to_clear.update(manager.keys())

    with tempfile.TemporaryDirectory(prefix="envprobe-community-kb-") as tempd:
        sources = downloader.download_latest_data(tempd)
        for source in sources:
            print("Extracting '{}'...".format(source.name))
            try:
                source.parse()
            except Exception as e:
                print("[WARN] Failed to parse '{}':\t{}"
                      .format(source.name, str(e)),
                      file=sys.stderr)
                continue

            storage_cfg.set_comment_for(source.name, source.comment)
            set_vars = 0
            for variable in source:
                information = EnvVarExtendedInformation()
                information.apply(source[variable])

                try:
                    manager = local_data.get_variable_information_manager(
                        variable, read_only=False)
                    manager.set(variable, information, source.name)
                    set_vars += 1

                    try:
                        variables_to_clear.remove(variable)
                    except KeyError:
                        pass
                except Exception as e:
                    print("[WARN] Failed to update configuration for "
                          "'{}':\t{}".format(variable, str(e)),
                          file=sys.stderr)
                    continue
            print("\textracted {} variables.".format(set_vars))

    print("Cleaning up old information...")
    set_vars = 0
    for variable in variables_to_clear:
        try:
            manager = local_data.get_variable_information_manager(
                variable, read_only=False)
            del manager[variable]
            set_vars += 1
        except Exception as e:
            print("[WARN] Failed to clean up '{}':\t{}".format(variable,
                                                               str(e)),
                  file=sys.stderr)
    print("\tcleaned up {} records.".format(set_vars))

    storage_cfg.version = new_version


def register_update(argparser):
    parser = argparser.add_parser(
            name=update_name,
            description=update_description,
            help=update_help,
            epilog=epilogue
    )

    parser.set_defaults(func=update_command)


def register(argparser, shell):
    parser = argparser.add_parser(
            name=name,
            description=description,
            help=help,
            epilog=epilogue
    )
    subparsers = parser.add_subparsers(
        title="available_commands")

    register_update(subparsers)
