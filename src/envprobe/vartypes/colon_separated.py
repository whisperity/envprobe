from .array import Array
from .envvar import register_type


class ColonSeparatedArray(Array):
    """A helper class that binds the array's `separator` to ``:``."""
    def __init__(self, name, raw_value):
        super().__init__(name, raw_value, ':')

    @classmethod
    def type_description(cls):
        """A list of strings in an array, separated by :"""
        return "A list of strings in an array, separated by :"


register_type('colon_separated', ColonSeparatedArray)
