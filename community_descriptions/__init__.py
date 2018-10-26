"""
Provides methods that connect an Envprobe install to the community
description project, fetching variable types and descriptions from a
crowdsourced project.
"""
import json
import os
import sys

from configuration import get_configuration_folder


def get_description(variable_name):
    """
    Retrieve the description for the variable :param:`variable_name`.
    """
    description = {'source': None,
                   'type': None,
                   'description': None}

    level_folder = os.path.join(get_configuration_folder(),
                                'descriptions',
                                variable_name[0].lower(),
                                variable_name[:2].lower())
    if not os.path.isdir(level_folder):
        return description

    describe_file = os.path.join(level_folder,
                                 variable_name[2].lower()) + '.json'
    local_file = os.path.join(level_folder,
                              variable_name[2].lower()) + '-local.json'

    # The user's local configuration should take priority.
    try:
        with open(local_file, 'r') as f:
            d = json.load(f)
            description.update(d.get(variable_name, dict()))
            description['source'] = 'local'
    except OSError:
        # If not found, ignore the error.
        pass

    if description:
        return description

    try:
        with open(describe_file, 'r') as f:
            d = json.load(f)
            description.update(d.get(variable_name, dict()))
    except OSError:
        # If not found, ignore the error.
        pass

    return description


def save_description(variable_name, description=None):
    """
    Save the description parameters for :param:`variable_name`. Saving can
    only happen to the user's "local" files, not the remotely fetched ones.
    """
    level_folder = os.path.join(get_configuration_folder(),
                                'descriptions',
                                variable_name[0].lower(),
                                variable_name[:2].lower())
    if not os.path.isdir(level_folder):
        os.makedirs(level_folder)

    local_file = os.path.join(level_folder,
                              variable_name[2].lower()) + '-local.json'

    d = dict()
    try:
        with open(local_file, 'r') as f:
            d = json.load(f)
    except (OSError, json.JSONDecodeError):
        # If not found, ignore the error.
        pass

    d[variable_name] = dict()
    if description['type']:
        d[variable_name]['type'] = description['type']
    if description['description']:
        d[variable_name]['description'] = description['description']

    try:
        with open(local_file, 'w') as f:
            json.dump(d, f)
    except (TypeError, ValueError) as e:
        # If not found, ignore the error.
        print("Error! Couldn't save the description: %s" % e)
        sys.exit(1)
