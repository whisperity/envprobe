"""
Provides methods that connect an Envprobe install to the community
description project, fetching variable types and descriptions from a
crowdsourced project.
"""
import json
import os

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
