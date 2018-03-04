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
    references, such as "~/foo/bar/../lib/c" into absolute paths. This is
    done by calling :func:`os.path.abspath`, so symbolic links are NOT
    resolved.
    """

    def _transform_element_set(self, elem):
        elem = super()._transform_element_set(elem)
        elem = os.path.expanduser(elem)
        elem = os.path.abspath(elem)

        return elem


register_type('path', PathLikeEnvVar)
