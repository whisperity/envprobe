"""
Implementation of PATH arrays.
"""
import os

from . import register_type
from .array import ColonSeparatedArray


class PathLike(ColonSeparatedArray):
    """
    Represents as POSIX PATH-like environment variable. `PATH` variables
    are commonly used as list of locations in a precedence order for finding
    various system elements. Commonly, `PATH`-like environment variables are
    separated by a `:`.

    This class provides the extra functionality above
    :type:`ColonSeparatedArrayEnvVar` in automatically converting relative
    references, such as "~/foo/bar/../lib/c" into absolute paths. This does
    not resolve symbolic links or expand variables, only removes unnecessary
    references, and prefixes the working directory.
    """

    def _transform_element_set(self, elem):
        elem = super()._transform_element_set(elem)

        if elem:
            elem = os.path.abspath(elem)

        return elem

    @staticmethod
    def type_description():
        return "A list of files and folders separated by : This type "        \
               "offers additional benefits in knowing that path entries can " \
               "be normalised and shortened."


register_type('path', PathLike)
