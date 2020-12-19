"""
This module contains the object model for environmental variable type classes.
"""
import importlib

ENVTYPE_CLASSES_TO_NAMES = {}
ENVTYPE_NAMES_TO_CLASSES = {}


def register_type(kind, clazz):
    """
    Register the given :type:`Shell` subtype for the given name in the
    module's table.
    """
    ENVTYPE_CLASSES_TO_NAMES[clazz] = kind
    ENVTYPE_NAMES_TO_CLASSES[kind] = clazz


def get_class(kind):
    """
    Returns the :type:`EnvVar` subtype for the given kind.
    """
    return ENVTYPE_NAMES_TO_CLASSES[kind]


def get_kind(clazz):
    """
    Returns the textual kind identifier for the :type:`EnvVar` subtype.
    """
    return ENVTYPE_CLASSES_TO_NAMES[clazz]


def load(kind):
    """
    Tries to load the given `kind` module from the current package and
    have it registered as a valid environment variable type implementation.

    If the type is registered, it is (the class) returned.
    """
    try:
        return get_class(kind)
    except KeyError:
        pass

    try:
        importlib.import_module("envprobe.vartypes.%s" % kind)
        # The loading of the module SHOULD register the type.
    except ModuleNotFoundError:
        raise KeyError("Environment variable type '%s' is not supported by "
                       "the current version."
                       % kind)

    return ENVTYPE_NAMES_TO_CLASSES.get(kind, None)


# Now that the top-level hierarchy for the loader is set, automatically load
# and expose to the user the base class definition.
from . import envvar  # noqa
