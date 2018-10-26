"""
Handles the configuration of mapping the user's preference on what
:module:`vartype` an environment variable should be.
"""

import os

from . import get_configuration_folder
from .locking_configuration_json import LockingConfigurationJSON


class VariableTypeMap(LockingConfigurationJSON):
    """
    Represents a configuration of variable names to :module:`vartype` types.

    This class is expected to be used as a context.
    """

    def __init__(self, read_only=False):
        super().__init__(os.path.join(get_configuration_folder(),
                                      'types.json'),
                         read_only=read_only,
                         default=dict())
