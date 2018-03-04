"""
This module contains the object model for environmental variable type classes.
"""

from abc import ABCMeta, abstractmethod


ENVTYPE_CLASSES_TO_NAMES = {}
ENVTYPE_NAMES_TO_CLASSES = {}


class EnvVarType(metaclass=ABCMeta):
    """
    The base class for an environmental variable. Provides the interface for
    understanding what an environmental variable is.
    """

    @abstractmethod
    def __init__(self, name, env_string):
        """
        Initializes an environmental variable from the given env_string,
        which is the raw value of the environmental variable read from the
        shell.
        """

        self._name = name

    @property
    def name(self):
        """
        Get the variable name of the current environment variable.
        """
        return self._name

    @abstractmethod
    def to_raw_var(self):
        """
        Converts the current environmental variable back into a raw value
        which then can be understood by the shell.
        """
        pass


# Expose the known type of environmental variables from the module.
__all__ = ['string', 'numeric', 'array']


def register_type(kind, clazz):
    """
    Register the given :type:`Shell` subtype for the given name in the
    module's table.
    """
    ENVTYPE_CLASSES_TO_NAMES[clazz] = kind
    ENVTYPE_NAMES_TO_CLASSES[kind] = clazz
