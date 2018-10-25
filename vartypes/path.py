import os

from . import array, register_type


class PathLikeEnvVar(array.ColonSeparatedArrayEnvVar):
    """
    Represents as POSIX PATH-like environmental variable. `PATH` variables
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


register_type('path', PathLikeEnvVar)
