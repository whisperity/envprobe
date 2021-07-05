"""
Provides methods that connect an Envprobe install to the community
description project, fetching variable types and descriptions from a
crowdsourced project.
"""
import csv
import io
import json
import os
import sys
import urllib.request
import tempfile
import zipfile

from configuration import get_configuration_folder


def get_description(variable_name):
    """
    Retrieve the description for the variable :param:`variable_name`.
    """
    description = {'source': None,
                   'type': None,
                   'description': None}

    first = variable_name[0].lower()
    second = variable_name[:2].lower() if len(variable_name) >= 2 else \
        'NULL'
    third = variable_name[2].lower() if len(variable_name) >= 3 else \
        'NULL'

    level_folder = os.path.join(get_configuration_folder(),
                                'descriptions',
                                first, second)
    if not os.path.isdir(level_folder):
        return description

    describe_file = os.path.join(level_folder, third) + '.json'
    local_file = os.path.join(level_folder, third) + '-local.json'

    # The user's local configuration should take priority.
    try:
        with open(local_file, 'r') as f:
            d = json.load(f)
            description.update(d.get(variable_name, dict()))
            description['source'] = 'local'

            return description
    except OSError:
        # If not found, ignore the error.
        pass

    try:
        with open(describe_file, 'r') as f:
            d = json.load(f)
            description.update(d.get(variable_name, dict()))

            return description
    except OSError:
        # If not found, ignore the error.
        pass

    return description


def extract_csv(filename, handle):
    """
    Read the given CSV file from the description database and transform it
    into the user's storage.
    """
    reader = csv.reader(handle, delimiter=';')
    header = []
    template = dict()

    for row in reader:
        if len(row) > 0 and row[0][0] == '#':
            # Ignore comments.
            continue

        if not template:
            # If the template has not been read yet, create it.
            header = row
            for key in row:
                template[key] = None
            continue

        row_var = dict(template)
        for idx, val in enumerate(row):
            row_var[header[idx]] = val

        variable = row_var[header[0]]
        del row_var[header[0]]
        row_var['source'] = os.path.splitext(
            os.path.basename(filename))[0]
        save_description(variable, row_var, local=False)


def get_description_release():
    """
    Download the latest version of the environment variable knowledgebase,
    and update the user's configuration files with the information.
    """
    print("Checking for latest knowledge-base...")
    response = urllib.request.urlopen(
        'http://api.github.com/repos/%s/%s/git/refs'
        % ('whisperity', 'envprobe-descriptions'))
    api = json.loads(response.read().decode('utf-8'))[0]
    current_sha = api['object']['sha']

    try:
        with open(os.path.join(get_configuration_folder(),
                               'descriptions', 'commit.sha'), 'r') as handle:
            known_sha = handle.read().strip()
    except OSError:
        # Use an invalid SHA if no "latest downloaded commit" was found
        # locally.
        known_sha = 'x' * 41

    if known_sha == current_sha:
        print("Nothing to update - latest knowledge-base is already "
              "downloaded.")
        return

    # Download the newest version of the knowledge-base and use it to update
    # the local structure.
    data = urllib.request.urlopen(
        'http://api.github.com/repos/%s/%s/zipball/master'
        % ('whisperity', 'envprobe-descriptions'))
    with tempfile.TemporaryFile('rb+', prefix='envprobe-kb-') as temp:
        temp.write(data.read())
        temp.seek(0)

        with zipfile.ZipFile(temp, 'r') as zipf:
            for entry in zipf.namelist():
                if not entry.endswith('csv'):
                    # Skip non-CSV files.
                    continue

                with io.TextIOWrapper(zipf.open(entry, 'r'),
                                      encoding='utf-8') as csv_file:
                    print("Extracting '%s'..." % os.path.basename(entry))
                    extract_csv(entry, csv_file)

        with open(os.path.join(get_configuration_folder(),
                               'descriptions', 'commit.sha'), 'w') as handle:
            handle.write(current_sha + "\n")
