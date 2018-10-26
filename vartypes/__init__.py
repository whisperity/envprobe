"""
This module contains the object model for environmental variable type classes.
"""

from abc import ABCMeta, abstractmethod


ENVTYPE_CLASSES_TO_NAMES = {}
ENVTYPE_NAMES_TO_CLASSES = {}


class EnvVar(metaclass=ABCMeta):
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

    @staticmethod
    def type_description():
        return "(Abstract base class for environment variables.)"

    @abstractmethod
    def to_raw_var(self):
        """
        Converts the current environmental variable back into a raw value
        which then can be understood by the shell.
        """
        pass

    @property
    @abstractmethod
    def value(self):
        """
        Retrieve the value of the environment variable as stored in Python.
        """
        pass

    @classmethod
    def get_difference(cls, old_variable, new_variable):
        """
        Generate an iterable of difference "actions" that can describe how
        the value of :param:`old_variable` can be transformed into
        :param:`new_variable`.
        """
        if type(old_variable) != type(new_variable):
            raise TypeError("Only variables of the same type can be "
                            "differentiated.")

        return {'type': type(old_variable).__name__,
                'diff': []}


# Expose the known type of environmental variables from the module.
__all__ = ['string', 'numeric', 'array', 'path']


def register_type(kind, clazz):
    """
    Register the given :type:`Shell` subtype for the given name in the
    module's table.
    """
    ENVTYPE_CLASSES_TO_NAMES[clazz] = kind
    ENVTYPE_NAMES_TO_CLASSES[kind] = clazz
