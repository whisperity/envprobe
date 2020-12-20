"""
This module contains the support code that translates envprobe operations to
shell operations.
"""
import importlib
import os

SHELL_CLASSES_TO_TYPES = {}
SHELL_TYPES_TO_CLASSES = {}


def register_type(kind, clazz):
    """
    Register the given :type:`Shell` subtype for the given name in the
    module's table.
    """
    SHELL_CLASSES_TO_TYPES[clazz] = kind
    SHELL_TYPES_TO_CLASSES[kind] = clazz


def get_class(kind):
    """
    Returns the :type:`Shell` subtype for the given kind.
    """
    return SHELL_TYPES_TO_CLASSES[kind]


def get_kind(clazz):
    """
    Returns the textual kind identifier for the :type:`Shell` subtype.
    """
    return SHELL_CLASSES_TO_TYPES[clazz]


def load(kind):
    """
    Tries to load the given `kind` module from the current package and
    have it registered as a valid shell.

    If the shell is registered, the type (class) is returned.
    """
    try:
        return get_class(kind)
    except KeyError:
        pass

    try:
        importlib.import_module("envprobe.shell.%s" % kind)
        # The loading of the module SHOULD register the type.
    except ModuleNotFoundError:
        raise NotImplementedError(
                "Shell '%s' is not supported by the current version."
                % kind)

    return SHELL_TYPES_TO_CLASSES.get(kind, None)


def load_all():
    """
    Loads every shell type implementation available to the interpreter.
    """
    for f in os.listdir(os.path.dirname(__loader__.path)):
        try:
            load(f.split('.')[0])
        except NotImplementedError:
            pass


# Now that the top-level hierarchy for the loader is set, automatically load
# and expose to the user the base class definition.
from . import shell  # noqa
