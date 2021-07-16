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
"""
Provides methods that connect an Envprobe install to the community descriptions
project, and handles downloading and installing the new knowledge-base.
"""
import csv
import json
import os
import urllib.request
import zipfile

from envprobe.compatibility import Version
from envprobe.settings import variable_information as vi


# Note: Please leave these as strings!
# This is unfortunately needed so that the documentation generates correctly.

MIN_SUPPORTED_FORMAT = "1.0"
"""The minimum version of description releases that is supported by the
current implementation."""

MAX_SUPPORTED_FORMAT = "1.0"
"""The maximum version of description releases that is supported by the
current implementation."""


REPOSITORY_USER = "whisperity"
REPOSITORY_NAME = "Envprobe-Descriptions"
REPOSITORY_BRANCH = "master"


class DescriptionSource:
    """The handler class that is used to parse and understand the files of the
    downloaded knowledge-base.
    """
    def __init__(self, source_file_path):
        """
        Parameters
        ----------
        source_file_path : str
            The path to the CSV database.

        Note
        ----
        Instantiating the object is a cheap operation.
        To load the data, call the :py:meth:`parse` method.
        """
        self._name = os.path.basename(source_file_path).replace(".csv", "")
        self._file = source_file_path
        self._data = dict()

        self._comment = None

    @property
    def name(self):
        """The identifier of the source."""
        return self._name

    @property
    def comment(self):
        """A textual comment about the contents of the source."""
        return self._comment

    def parse(self):
        """Execute loading of the data from the backing file."""
        with open(self._file, 'r') as handle:
            reader = csv.DictReader(handle)
            for record in reader:
                if record["Variable"] == "__META__":
                    self._handle_meta_record(record)
                    continue

                self._data[record["Variable"]] = \
                    self._transform_to_configuration_record(record)

    def _handle_meta_record(self, record):
        if record["TypeKind"] == "COMMENT":
            self._comment = record["Description"]
            return

    def _transform_to_configuration_record(self, record):
        """Transforms the given CSV record to a configuration record
        appropriate for
        :py:class:`envprobe.settings.variable_information.VariableInformation`.
        """
        return {vi.K_VARIABLE_DESCRIPTION: record["Description"],
                vi.K_VARIABLE_TYPE: record["TypeKind"]
                }

    def __len__(self):
        """The number of variables in the source."""
        return len(self._data)

    def __iter__(self):
        """Iterate over the variables in the source."""
        return iter(self._data.keys())

    def __getitem__(self, variable):
        """Get the information for the given `variable`.

        Returns
        -------
        : dict
            The configuration mapping of the variable as parsed from the source
            file.
            The format of the dictionary is appropriate for use with
            :py:class:`envprobe.vartypes.envvar.EnvVarExtendedInformation`.
        """
        return self._data[variable]


def fetch_latest_version_information():
    """Obtain the version of the latest downloadable knowledge base.

    Note
    ----
    Executing this function **requires** Internet connection, and will make a
    connection to GitHub's API.

    Raises
    ------
    URLError
        Executing the request may fail due to configuration issues, bad
        connection, or GitHub API's throttling of the user.
        Throttling is implemented for unauthenticated requests against the
        IP address of the machine.
        Read more at http://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting.
    """  # noqa: E501  # Ignore the overflowing URL.
    response = urllib.request.urlopen(  # nosec: urllib
        "http://api.github.com/repos/{}/{}/git/refs"
        .format(REPOSITORY_USER, REPOSITORY_NAME))
    result = json.loads(response.read().decode("utf-8"))

    for ref_entry in result:
        if ref_entry["ref"] == "refs/heads/{}".format(REPOSITORY_BRANCH):
            return ref_entry["object"]["sha"]


def download_latest_data(location):
    """Downloads the latest information to the given location.

    Parameters
    ----------
    location : str
        The path the downloader can use to extract the data to.
        This directory **must exist** already, and will not be cleared up by
        this function.
        This is only used temporarily.

    Returns
    -------
    list(.DescriptionSource)
        The handlers of the extracted knowledge source documents.

    Note
    ----
    Executing this function **requires** Internet connection, and will make a
    connection to GitHub's API.

    Raises
    ------
    URLError
        Executing the request may fail due to configuration issues, bad
        connection, or GitHub API's throttling of the user.
        Throttling is implemented for unauthenticated requests against the
        IP address of the machine.
        Read more at http://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting.
    """  # noqa: E501  # Ignore the overflowing URL.
    data = urllib.request.urlopen(  # nosec: urllib
        "http://api.github.com/repos/{0}/{1}/zipball/{2}"
        .format(REPOSITORY_USER, REPOSITORY_NAME, REPOSITORY_BRANCH))

    output = os.path.join(location, "release.zip")
    with open(output, 'wb') as handle:
        handle.write(data.read())

    extracted = list()
    with zipfile.ZipFile(output, 'r') as handle:
        min_ver = Version(MIN_SUPPORTED_FORMAT)
        max_ver = Version(MAX_SUPPORTED_FORMAT)
        try:
            format_file = next(filter(lambda f:
                                      os.path.basename(f) == "format.ver",
                                      handle.namelist()))
            format = Version(handle.read(format_file).decode("utf-8"))
        except StopIteration:
            format = Version(None)

        if format < min_ver:
            raise ValueError("Unable to understand description release. "
                             "Version {0} is older than oldest supported {1}"
                             .format(format, min_ver))
        if format > max_ver:
            raise ValueError("Unable to understand description release. "
                             "Version {0} is newer than newest supported {1}"
                             .format(format, max_ver))

        for element in handle.namelist():
            if not element.endswith(".csv"):
                continue

            output_path = os.path.join(location, os.path.basename(element))
            with handle.open(element, 'r') as source, \
                    open(output_path, 'w') as target:
                target.write(source.read().decode("utf-8"))

            if element.endswith(".csv"):
                extracted.append(DescriptionSource(output_path))

    return extracted
