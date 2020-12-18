"""
This module contains the object model for environmental variable type classes.
"""

ENVTYPE_CLASSES_TO_NAMES = {}
ENVTYPE_NAMES_TO_CLASSES = {}


# Expose the known type of environmental variables from the module.
__all__ = ['string', 'numeric', 'array', 'path']


def register_type(kind, clazz):
    """
    Register the given :type:`Shell` subtype for the given name in the
    module's table.
    """
    ENVTYPE_CLASSES_TO_NAMES[clazz] = kind
    ENVTYPE_NAMES_TO_CLASSES[kind] = clazz
