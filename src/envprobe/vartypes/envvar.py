"""
Defines the abstract base class for all environment variable types.
"""
from abc import ABCMeta, abstractmethod


class EnvVar(metaclass=ABCMeta):
    """
    The base class for an environment variable.

    Provides the interface for understanding what an environment variable is.
    """

    @abstractmethod
    def __init__(self, name, env_string):
        """
        Initializes an environment variable from the given env_string,
        which is the raw value of the environmentvariable read from the
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
        Converts the current environment variable back into a raw value
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
