"""
Implementation of PATH arrays.
"""
import os

from . import register_type
from .colon_separated import ColonSeparatedArray


class Path(ColonSeparatedArray):
    """A POSIX-compatible ``PATH`` environment variable.

    ``PATH`` variables are commonly used as list of locations (directories,
    and, rarely, files) on the filesystem in an order of precedence for finding
    various system elements. ``PATH`` variables in POSIX are separated by
    ``:``, except in rare circumstances.

    This class extends :py:class:`ColonSeparatedArray` with automatically
    converting the given paths (when the array is constructed or modified) to
    **absolute paths**, by calling :py:func:`os.abspath` on the value.
    Symbolic links are kept and variable sequences such as ``~`` remain
    unexpanded, however, relative references (``a/../b`` to ``b``) are removed
    and the current working directory (:py:func:`os.getcwd`) is prepended.
    """
    def __init__(self, name, raw_value):
        """Create a :py:class:`Path` from the given `raw_value`."""
        super().__init__(name, raw_value)

    def _transform_element_set(self, elem):
        """Transforms the `elem` to an absolute path."""
        elem = super()._transform_element_set(elem)
        if elem:
            elem = os.path.abspath(elem)
        return elem

    @classmethod
    def type_description(cls):
        """A list of directories (and sometimes files) separated by :, and
        automatically expanded to absolute paths."""
        return "A list of directories (and sometimes files) separated by :, " \
               "and automatically expanded to absolute paths."""


register_type('path', Path)
