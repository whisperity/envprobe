from . import register_type
from .array import Array


class ColonSeparatedArray(Array):
    """
    Represents an environment variable in which array elements are
    separated by `:`.
    """

    def __init__(self, name, env_string):
        super().__init__(name, env_string, ':')

    @staticmethod
    def type_description():
        return "A list of string variables in an array, separated by :"


register_type('colon_separated', ColonSeparatedArray)
