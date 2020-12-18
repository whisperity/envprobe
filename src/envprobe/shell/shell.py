from abc import ABCMeta, abstractmethod
import importlib
import os

from . import SHELL_TYPES_TO_CLASSES, SHELL_CLASSES_TO_TYPES


class Shell(metaclass=ABCMeta):
    """
    The base class of a system shell.
    """

    def __init__(self, pid, location, config_dir):
        self._shell_pid = pid
        self._envprobe_location = location
        self._configuration_dir = config_dir

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
    def configuration_directory(self):
        """
        :return: The directory where the :type:`Shell` instance's controlling
        data is kept. This is in all cases a temporary directory used by the
        hooks.
        """
        return self._configuration_dir

    @property
    def control_file(self):
        """
        Returns the location of the shell hook's control file.
        """
        return os.path.join(self.configuration_directory, 'control.sh')

    @property
    def state_file(self):
        """
        Returns the path of the file which is used to save the "known" state
        of the shell.
        """
        # TODO: Pickle is a bit outdated and sometimes insecure, we need to use
        #       a better serialisation method.
        return os.path.join(self._configuration_directory, 'state.pickle')

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
        # TODO: Some locking should be done here.
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


def get_current_shell():
    """
    Creates a Shell instance based on the current environment, if possible.

    Returns False if the current shell type is unknown or None if the user
    does not have envprobe enabled.
    """
    shell_type = os.environ.get('ENVPROBE_SHELL_TYPE')
    if not shell_type:
        return None

    clazz = SHELL_TYPES_TO_CLASSES.get(shell_type)
    if not clazz:
        try:
            importlib.import_module("envprobe.shell.%s" % shell_type)
            # The loading of the module SHOULD register the type.
        except ModuleNotFoundError:
            raise KeyError("Shell '%s' is not supported by the current "
                           "version." % shell_type)

    clazz = SHELL_TYPES_TO_CLASSES.get(shell_type)
    if not clazz:
        raise NotImplementedError("Shell '%s' failed to load.")

    shell = clazz(os.environ.get('ENVPROBE_SHELL_PID', None),
                  os.environ.get('ENVPROBE_LOCATION', None),
                  os.environ.get('ENVPROBE_CONFIG', None))

    return shell
