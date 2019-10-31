"""
This module contains the support code that translates envprobe operations to
shell operations.
"""

# TODO: Refactor the subcommands to a better layout, support dynamic loading.

from abc import ABCMeta, abstractmethod
import os


SHELL_CLASSES_TO_TYPES = {}
SHELL_TYPES_TO_CLASSES = {}


class Shell(metaclass=ABCMeta):
    """
    The base class of a system shell.
    """

    def __init__(self):
        self._shell_pid = None
        self._envprobe_location = None
        self._configuration_folder = None

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
    def shell_type(self):
        """
        Returns the current shell's type in a textual format.
        """
        return SHELL_CLASSES_TO_TYPES.get(type(self), "Unknown?")

    @property
    def shell_pid(self):
        """
        Returns the process ID of the shell that the user is currently
        using.
        """
        return self._shell_pid

    @property
    def envprobe_location(self):
        """
        Returns the absolute location where envprobe is installed.
        """
        return self._envprobe_location

    @property
    def configuration_folder(self):
        """
        :return: The directory where the :type:`Shell` instance's controlling
        data is kept. This is in all cases a temporary directory used by the
        hooks.
        """
        return self._configuration_folder

    @property
    def control_file(self):
        """
        Returns the location of the shell hook's control file.
        """
        return os.path.join(self._configuration_folder, 'control.sh')

    @property
    def state_file(self):
        """
        Returns the path of the file which is used to save the "known" state
        of the shell.
        """
        return os.path.join(self._configuration_folder, 'state.pickle')

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

    @abstractmethod
    def _prepare_setting_env_var(self, env_var):
        """
        This method specifies how a particular Shell can execute a command
        which sets the given :param:`env_var`'s value to be what the user
        intended in their shell.
        """
        pass

    @abstractmethod
    def _prepare_undefining_env_var(self, env_var):
        """
        This method specifies how a particular Shell can execute a command
        which undefines the given :param:`env_var`.
        """
        pass

    def set_env_var(self, env_var):
        """
        This method writes the given :param:`env_var`'s value to a special
        temporary file that is executed by the hooked Shell. The user's
        shell SHOULD, but maybe not immediately, reflect the change in the
        environment ordered by this method.
        """

        # This method SHOULD always assume that the temporary file's state is
        # unknown. Usually, the shell parses and destroys commands in the
        # temporary file at every prompt reading.
        with open(self.control_file, 'a') as control:
            control.write('\n')
            control.write(self._prepare_setting_env_var(env_var))
            control.write('\n')

    def undefine_env_var(self, env_var):
        """
        This method writes the given :param:`env_var`'s name into the control
        file that is executed by the current shell with the notion that the
        variable should be undefined, no matter what value it had.
        """
        with open(self.control_file, 'a') as control:
            control.write('\n')
            control.write(self._prepare_undefining_env_var(env_var))
            control.write('\n')


# Expose every shell known in this module.
__all__ = ['bash', 'zsh']


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
