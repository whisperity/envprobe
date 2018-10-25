import os


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
