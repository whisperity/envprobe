# Copyright (C) 2018 Whisperity
#
# SPDX-License-Identifier: GPL-3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Core functions of the shell library, such as the abstract base class
`Shell`, and the dynamic subclass loading.
"""
from abc import ABCMeta, abstractmethod
import importlib
import os


__SHELL_CLASSES_TO_TYPES = {}
__SHELL_TYPES_TO_CLASSES = {}


class CapabilityError(Exception):
    """Indicates that the requested operation cannot be done in the current
    Shell.
    """
    pass


class Shell(metaclass=ABCMeta):
    """Base class for keeping configuration related to a running shell."""

    def __init__(self, pid, configuration_dir, control_filename):
        """
        Parameters
        ----------
        pid : int
            The process ID (*pid*) of the shell.
        configuration_dir : str
            The directory where the control and persistent data of the shell
            process will be stored.
        control_filename : str
            The name of the file which is used by the hook to execute commands
            in the shell's context.
        """
        self._shell_pid = pid
        self._configuration_dir = configuration_dir
        self._control_filename = control_filename

    @property
    def shell_type(self):
        """The identifier of the shell's type as registered in Envprobe.
        """
        return get_kind(type(self))

    @property
    def shell_pid(self):
        """The `pid` the shell was constructed with."""
        return self._shell_pid

    @property
    def configuration_directory(self):
        """The `configuration_dir` the shell was constructed with.

        This is the directory where the data of the shell hook is written to
        on storage.

        Note
        ----
        In almost all cases, this is a temporary directory!
        """
        return self._configuration_dir

    @property
    def control_file(self):
        """The **full** path to the *control file* the shell was
        constructed with.

        The contents of this file are directives written in the target shell's
        syntax, and is used to apply the changes commandeered by Envprobe
        in the shell's context itself.
        """
        return os.path.join(self.configuration_directory,
                            self._control_filename)

    @property
    def state_file(self):
        """The full path of the file persisted in storage that is used to
        store the "saved" state and knowledge about the shell.
        """
        # TODO: Pickle is a bit outdated and sometimes insecure, we need to use
        #       a better serialisation method.
        return os.path.join(self.configuration_directory, 'state.pickle')

    @property
    @abstractmethod
    def is_envprobe_capable(self):
        """Whether the current shell is capable of loading and
        meaningfully running Envprobe.
        """
        pass

    @abstractmethod
    def get_shell_hook(self, envprobe_callback_location):
        """Create the shell code that drives Envprobe's control evaluation.

        This code should be evaluated inside the context of an existing shell
        process to faciliate execution of the `control_file`'s contents.
        """
        pass

    @abstractmethod
    def get_shell_unhook(self):
        """Create the shell code that detaches/unhooks Envprobe.

        This code should be evaluated inside the context of an existing shell
        process as an inverse operation of :py:func:`get_shell_hook`.
        """
        pass

    @property
    @abstractmethod
    def manages_environment_variables(self):
        """Whether the current shell is capable of managing the environment
        variables through Envprobe.
        """
        pass

    def _set_environment_variable(self, env_var):
        """Subclasses should override and provide the implementation for
        `set_environment_variables`.
        """
        raise NotImplementedError("_set_environment_variable should be "
                                  "implemented if the shell is capable for "
                                  "managing env vars.")

    def set_environment_variable(self, env_var):
        """Write the code setting `env_var`'s value to the `control_file`.

        Raises
        ------
        CapabilityError
            If the shell is not capable of managing environment variables.

        Note
        ----
        The implementation for the actual code writing should be provided in
        the overriden method :py:func:`_set_environment_variable` instead.
        """
        if not self.manages_environment_variables:
            raise CapabilityError("Can't manage environment variables.")
        return self._set_environment_variable(env_var)

    def _unset_environment_variable(self, env_var):
        """Subclasses should override and provide the implementation for
        `unset_environment_variables`.
        """
        raise NotImplementedError("_unset_environment_variable should be "
                                  "implemented if the shell is capable for "
                                  "managing env vars.")

    def unset_environment_variable(self, env_var):
        """Write the code that undefines `env_var` to the `control_file`.

        Raises
        ------
        CapabilityError
            If the shell is not capable of managing environment variables.

        Note
        ----
        The implementation for the actual code writing should be provided in
        the overriden method :py:func:`_unset_environment_variable` instead.
        """
        if not self.manages_environment_variables:
            raise CapabilityError("Can't manage environment variables")
        return self._unset_environment_variable(env_var)


class FakeShell(Shell):
    """A fake :py:class:`Shell` that provides the interface and is a proper
    subclass, but does not offer any meaningful functionality.

    Note
    ----
    This class is **not** available through :py:func:`shell.load` and is not
    registered into the dynamic loading infrastructure.
    """
    def __init__(self):
        super().__init__(-1, os.path.curdir, "null.txt")

    @property
    def shell_type(self):
        return "__fake__"

    @property
    def control_file(self):
        return os.path.devnull

    @property
    def state_file(self):
        return os.path.devnull

    @property
    def is_envprobe_capable(self):
        return False

    def get_shell_hook(self, envprobe_callback_location):
        return ""

    def get_shell_unhook(self):
        return ""

    @property
    def manages_environment_variables(self):
        return False


def register_type(kind, clazz):
    """Register the :py:class:`Shell` implementation to the dynamic lookup
    mechanism.

    Parameters
    ----------
    kind : str
        The name of the shell implementation.
    clazz : class
        The Python class that implements the functions.

    Raises
    ------
    TypeError
        `clazz` must be a type that is a subclass of `Shell`, otherwise an
        exception is raised.

    Example
    -------
    The implementing modules of :py:class:`Shell` subclasses should be named
    similarly as the shell they are implementing, and after defining the
    ``class``, in the global code of the module itself, a call to
    `register_type` should be present:

    .. code-block:: py
        :caption: Registering a hypothetical implementation of the PytShell in
            ``envprobe.shell.pyt``

        from envprobe.shell.core import Shell, register_type

        class Pyt(Shell):
            # ... the implementation of the class ...

        register_type('pyt', Pyt)
    """
    if not issubclass(clazz, Shell):
        raise TypeError("{0} is not a Shell".format(str(clazz)))
    __SHELL_CLASSES_TO_TYPES[clazz] = kind
    __SHELL_TYPES_TO_CLASSES[kind] = clazz


def get_class(kind):
    """Retrieves the implementation class for the given name from the dynamic
    registry.

    Parameters
    ----------
    kind : str
        The name of the shell, as registered.

    Returns
    -------
    class
        The class implementation.

    Raises
    ------
    KeyError
        Raised if the given `kind` is not registered.
    """
    return __SHELL_TYPES_TO_CLASSES[kind]


def get_kind(clazz):
    """Retrieves the name for the given implementation class from the
    dynamic registry.

    Parameters
    ----------
    clazz : class
        The implementation `class` object.

    Returns
    -------
    str
        The registered name for the implementation.

    Raises
    ------
    KeyError
        Raised if the given `clazz` is not registered.
    """
    return __SHELL_CLASSES_TO_TYPES[clazz]


def get_known_kinds():
    """Get the list of dynamically registered and loaded :py:class:`Shell`
    implementations.

    Returns
    -------
    list(str)
        The names.
    """
    return __SHELL_TYPES_TO_CLASSES.keys()


def load(kind):
    """Attempt to load a :py:class:`Shell` implementation.

    The function loads the module `kind` from :py:mod:`envprobe.shell` an
    expects it to register the :py:class:`Shell` named `kind`.

    Parameters
    ----------
    kind : str
        The name of the shell to load.
        The loading will be done from the similarly named Python module under
        :py:mod:`envprobe.shell`.

    Returns
    -------
    clazz : class
        If the loading succeeded or the given `kind` is already loaded, the
        class implementation is returned.

    Raises
    ------
    ModuleNotFoundError
        Raised if the module to load is not found.
    NotImplementedError
        Raised if the module successfully loaded, but there were no shell with
        the name `kind` registered by it.
    """
    try:
        return get_class(kind)
    except KeyError:
        pass

    try:
        importlib.import_module("envprobe.shell.{0}".format(kind))
    except ModuleNotFoundError:
        raise

    try:
        # The loading of the module SHOULD register the type.
        return get_class(kind)
    except KeyError:
        raise NotImplementedError("envprobe.shell.{0} did not register '{0}'".
                                  format(kind))


def load_all():
    """Loads all :py:class:`Shell` implementations to the interpreter found
    under :py:mod:`envprobe.shell` in the install.

    This method does not throw if a module does not actually register anything.
    """
    for f in os.listdir(os.path.dirname(__loader__.path)):
        module_name = f.split('.')[0]
        if not (module_name and f.endswith('.py')):
            continue
        try:
            load(module_name)
        except NotImplementedError:
            pass


def get_current_shell(environment_dict):
    """Create a :py:class:`Shell` based on the configured environment
    variables.

    Returns
    -------
    Shell
        The :py:class:`Shell` is instantiated with the environment settings.

    Raises
    ------
    KeyError
        Raised if the `environment_dict` did not contain the necessary
        variables configured.
    ModuleNotFoundError
        Raised if the shell to be used was identified, but the implementation
        was unable to load.
    """
    try:
        shell_type = environment_dict["ENVPROBE_SHELL_TYPE"]
    except KeyError:
        raise

    clazz = None
    try:
        clazz = get_class(shell_type)
    except KeyError:
        try:
            clazz = load(shell_type)
        except (ModuleNotFoundError, NotImplementedError):
            raise ModuleNotFoundError("{0} failed to load.".format(shell_type))

    return clazz(environment_dict.get("ENVPROBE_SHELL_PID"),
                 environment_dict.get("ENVPROBE_CONFIG"))
