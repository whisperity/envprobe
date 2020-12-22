"""
This module contains the object model for environmental variable type classes.
"""
import importlib
import os

ENVTYPE_CLASSES_TO_NAMES = {}
ENVTYPE_NAMES_TO_CLASSES = {}


def register_type(kind, clazz):
    """
    Register the given :type:`EnvVar` subtype for the given name in the
    module's table.
    """
    ENVTYPE_CLASSES_TO_NAMES[clazz] = kind
    ENVTYPE_NAMES_TO_CLASSES[kind] = clazz


def get_class(kind):
    """
    :return: The :type:`EnvVar` subtype for the given kind.
    """
    return ENVTYPE_NAMES_TO_CLASSES[kind]


def get_kind(clazz):
    """
    :return: The textual kind identifier for the :type:`EnvVar` subtype.
    """
    return ENVTYPE_CLASSES_TO_NAMES[clazz]


def get_known_kinds():
    """
    :return: The list of :type:`EnvVar` subtype names that are loaded.
    """
    return ENVTYPE_NAMES_TO_CLASSES.keys()


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
        raise NotImplementedError(
                "Environment variable type '%s' is not supported by the "
                "current version."
                % kind)

    return ENVTYPE_NAMES_TO_CLASSES.get(kind, None)


def load_all():
    """
    Loads every environment variable type implementation available to the
    interpreter.
    """
    for f in os.listdir(os.path.dirname(__loader__.path)):
        try:
            load(f.split('.')[0])
        except NotImplementedError:
            pass


# Now that the top-level hierarchy for the loader is set, automatically load
# and expose to the user the base class definition.
from . import envvar  # noqa
