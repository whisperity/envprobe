"""
Definition of the abstract base class for Shells.
"""

from abc import ABCMeta, abstractmethod
import os

from . import get_class, get_kind, load


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
        return get_kind(type(self))

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
        return os.path.join(self.configuration_directory, 'state.pickle')

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


class FakeShell(Shell):
    """
    Implements a fake :type:`Shell`, which provides all the methods necessary
    to be a proper subclass but with guarding against useful facilities.
    """
    def __init__(self):
        super().__init__(-1, os.path.curdir, os.path.curdir)

    @property
    def shell_type(self):
        return ""

    @property
    def control_file(self):
        return os.path.devnull

    @property
    def state_file(self):
        return os.path.devnull

    def is_envprobe_capable(self):
        return False

    def get_shell_hook(self):
        return ""

    def get_shell_hook_error(self):
        return ""

    def _prepare_setting_env_var(self, env_var):
        return ""

    def _prepare_undefining_env_var(self, env_var):
        return ""


def get_current_shell(environment_dict):
    """
    Creates a Shell instance based on the current environment mapping,
    if possible.

    Returns False if the current shell type is unknown or None if the user
    does not have envprobe enabled.
    """
    shell_type = environment_dict.get("ENVPROBE_SHELL_TYPE", None)
    if not shell_type:
        raise KeyError("Current shell's type is not configured.")

    clazz = None
    try:
        clazz = get_class(shell_type)
    except KeyError:
        clazz = load(shell_type)
        if not clazz:
            raise NotImplementedError("Shell '%s' failed to load.")

    shell = clazz(environment_dict.get("ENVPROBE_SHELL_PID"),
                  environment_dict.get("ENVPROBE_LOCATION"),
                  environment_dict.get("ENVPROBE_CONFIG"))

    return shell
