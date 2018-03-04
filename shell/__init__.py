"""
This module contains the support code that translates envprobe operations to
shell operations.
"""

from abc import ABCMeta, abstractmethod
import os


SHELL_CLASSES_TO_TYPES = {}
SHELL_TYPES_TO_CLASSES = {}


class Shell(metaclass=ABCMeta):
    """
    The base class of a system shell.
    """

    def __init__(self):
        pass

    @property
    def shell_type(self):
        """
        Returns the current shell's type in a textual format.
        """
        return SHELL_CLASSES_TO_TYPES.get(type(self), "Unknown?")

    @staticmethod
    def for_shell(shell_type):
        """
        Creates a Shell instance based on the given `shell_type`, if possible.
        This is approximately the inverse of the :func:`shell_type`: property.

        Returns none if the given `shell_type` is unknown.
        """
        clazz = SHELL_TYPES_TO_CLASSES.get(shell_type)
        if clazz:
            return clazz()

        return None

    @property
    @abstractmethod
    def shell_pid(self):
        """
        Returns the process ID of the shell that the user is currently
        using.
        """
        pass

    @property
    @abstractmethod
    def envprobe_location(self):
        """
        Returns the absolute location where envprobe is installed.
        """
        pass

    @abstractmethod
    def is_envprobe_capable(self):
        """
        Returns whether the current shell is capable of loading and running
        envprobe.
        """
        pass

    @abstractmethod
    def get_shell_hook(self):
        """
        Returns a string that is evaluated inside the shell directly. This
        code is used to set up the shell hook that enables the usage of
        envprobe.
        """
        pass

    @abstractmethod
    def get_shell_hook_error(self):
        """
        Returns a string that is evaluated inside the shell directly in case
        the environment does not allow envprobe to be set up.
        """
        pass


# Expose every shell known in this module.
__all__ = ['bash']


def register_type(kind, clazz):
    """
    Register the given :type:`Shell` subtype for the given name in the
    module's table.
    """
    SHELL_CLASSES_TO_TYPES[clazz] = kind
    SHELL_TYPES_TO_CLASSES[kind] = clazz


def get_current_shell():
    """
    Creates a Shell instance based on the current environment, if possible.

    Returns False if the current shell type is unknown or None if the user
    does not have envprobe enabled.
    """
    shell_type = os.environ.get('ENVPROBE_SHELL_TYPE')
    if not shell_type:
        return None

    shell = Shell.for_shell(shell_type)
    if not shell:
        return False

    return shell
