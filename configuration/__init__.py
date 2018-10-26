import os


__all__ = ['get_configuration_folder',
           'global_config',
           'locking_configuration_json',
           'tracked_variables',
           'variable_types']


def get_configuration_folder():
    """
    Retrieves the folder where the user's persistent configuration files
    should be saved.
    """
    return os.path.join(
        os.path.expanduser('~'),
        '.local',
        'share',
        'envprobe')
