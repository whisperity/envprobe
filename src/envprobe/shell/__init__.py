"""
This module contains the support code that translates envprobe operations to
shell operations.
"""

SHELL_CLASSES_TO_TYPES = {}
SHELL_TYPES_TO_CLASSES = {}


__all__ = ['shell']


def register_type(kind, clazz):
    """
    Register the given :type:`Shell` subtype for the given name in the
    module's table.
    """
    SHELL_CLASSES_TO_TYPES[clazz] = kind
    SHELL_TYPES_TO_CLASSES[kind] = clazz
