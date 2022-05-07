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
"""Implements the logic for interfacing with the environment's contents,
mapping variable primitives to internal data structure, keeping state, etc.
"""
from copy import deepcopy
from enum import Enum
import os
import pickle  # nosec: pickle has some issues, we will get back to it later.

from envprobe import vartypes


class EnvVarTypeHeuristic:
    """A heuristic maps a variable's name and it's potential value in the
    environment to an :py:mod:`envprobe.vartypes` type.
    """
    def __call__(self, name, env=None):
        """Resolve the variable of `name` (in the `env` environment) to an
        :py:mod:`envprobe.vartype` type identifier (as registered by
        :py:func:`.vartypes.register_type`).

        The default implementation resolves everything to be ``'string'``,
        corresponding to :py:class:`.vartypes.string.String`.

        Parameters
        ----------
        name : str
            The name of the environment variable.
        env : dict, optional
            The raw mapping of environment variables to their values, as in
            :py:data:`os.environ`.

        Returns
        -------
        vartype_name : str
            The name of an :py:mod:`envprobe.vartypes` implementation, if the
            heuristic resolved successfully.

        None
            ``None`` is returned if the heuristic could not resolve a type
            to be used.

        False : bool
            ``False`` is returned if the heuristic resolved the variable
            **not to be managed** by Envprobe.
        """
        return 'string'


class HeuristicStack:
    """A stack of :py:class:`EnvVarTypeHeuristic` objects which resolve a
    variable in a set order.

    Example
    -------
    .. code-block:: python

        # Build the pipeline.
        pipeline = HeuristicStack()
        pipeline += HeuristicThatAlwaysReturnsString()
        pipeline += HeuristicThatMapsTESTVarToFalse()

        # (HeuristicStack executes the added heuristics in reverse order.)

        # Use the pipeline to resolve.
        pipeline("TEST", env)
        >>> False

        pipeline("OTHER_VAR", env)
        >>> 'string'
    """
    def __init__(self):
        self._elements = list()

    def __add__(self, heuristic):
        """Add the `heuristic` to the top of the stack.

        Raises
        ------
        TypeError
            If `heuristic` isn't an :py:class:`EnvVarTypeHeuristic`.
        """
        if not isinstance(heuristic, EnvVarTypeHeuristic):
            raise TypeError("{0} != EnvVarTypeHeuristic".
                            format(str(type(heuristic))))
        self._elements.append(heuristic)
        return self

    def __call__(self, name, env=None):
        """Resolve the variable of `name` (in the `env` environment) to an
        :py:mod:`envprobe.vartype` type identifier, using the heuristics in
        the order of the stack.

        The resolution is run until a heuristic returns non-None (either
        ``False`` or an identifier).

        Parameters
        ----------
        name : str
            The name of the environment variable.
        env : dict, optional
            The raw mapping of environment variables to their values, as in
            :py:data:`os.environ`.

        Returns
        -------
        vartype_name : str
            The name of an :py:mod:`envprobe.vartypes` implementation, if a
            heuristic resolved successfully.

        None
            ``None`` is returned if no heuristic could resolve a type to use.

        False : bool
            ``False`` is returned if a heuristic resolved the variable
            **not to be managed** by Envprobe.
        """
        for h in reversed(self._elements):
            result = h(name, env)
            if result:
                return result
            if result is False:
                break
        return None


# Create the default type heuristic pipeline that only uses the default
# implementation.
default_heuristic = HeuristicStack()
"""Provides the default :py:class:`EnvVarTypeHeuristic` added to an
instantiated :py:class:`HeuristicStack`.

The default heuristic maps every variable to a pure
:py:class:`.vartypes.string.String`.
"""
default_heuristic += EnvVarTypeHeuristic()


def create_environment_variable(name, env, pipeline=None):
    """Create a :py:class:`.vartypes.EnvVar` instance for a variable, using a
    specific pipeline in an environment.

    Parameters
    ----------
    name: str
        The name of the environment variable to create.
    env : dict
        The raw mapping of environment variables to their values, as in
        :py:data:`os.environ`.
    pipeline : HeuristicStack, optional
        The heuristics pipeline to use to decide on the variable's type.
        If not specified, :py:data:`default_heuristic` is used.

    Returns
    -------
    .vartypes.EnvVar
        The instantiated environment variable.
        The variable is instantiated even if the variable is **not** found in
        `env`.

    Raises
    ------
    KeyError
        If the variable was not resolved to a valid type by the `pipeline`,
        either because no heuristic mapped to anything, or a heuristic mapped
        to ``False``.
    """
    if not pipeline:
        pipeline = default_heuristic

    kind = pipeline(name, env)
    if not kind:
        raise KeyError("Couldn't resolve '{0}' to a variable type."
                       .format(name))

    clazz = vartypes.load(kind)
    return clazz(name, env.get(name, ""))


class VariableDifferenceKind(Enum):
    """Named enumeration to indicate the "direction" of the
    :py:class:`VariableDifference`.
    """

    UNKNOWN = 0
    CHANGED = 1
    """The variable is defined on both sides ("old" and "new") of the
    difference, but to different values.
    """
    REMOVED = 2
    """The variable is defined in "old" but not defined in "new"."""
    ADDED = 3
    """The variable is not defined in "old" but defined in "new"."""


class VariableDifference:
    """The difference of a single variable between two states."""
    def __init__(self, kind, var_name, old_value=None, new_value=None,
                 difference_actions=None):
        """
        Parameters
        ----------
        kind : VariableDifferenceKind
            The "direction" of the difference's result.
        var_name : str
            The name of the variable that was differentiated.
        old_value : unknown
            The "old" value of the variable.
        new_value : unknown
            The "new" value of the variable.
        difference_actions : list(char, str)
            The individual changes in the variable's value, as returned by
            :py:meth:`.vartypes.EnvVar.diff`.

            The list contains the changes with a *mode* symbol (``-``, ``=``
            or ``+`` for *removed*, *unchanged/same*, *added*, respectively),
            and the value that was affected.

        Raises
        ------
        TypeError
            `kind` must be one of the constants in
            :py:class:`VariableDifferenceKind`.
        """
        if not isinstance(kind, VariableDifferenceKind):
            raise TypeError("'kind' must be a valid kind")

        self.kind = kind
        self.variable = var_name
        self.old_value = old_value
        self.new_value = new_value
        self.diff_actions = difference_actions if difference_actions \
            else list()

    @property
    def is_simple_change(self):
        """Whether the current instance represents a simple change.

        A simple change is either the creation or removal of a value, or a
        single-step modification of a value from one value to another.
        """
        return ((self.kind == VariableDifferenceKind.ADDED or
                self.kind == VariableDifferenceKind.REMOVED) and
                len(self.diff_actions) == 1) or \
            (len(self.diff_actions) == 2 and
                self.diff_actions[0] == ('-', self.old_value) and
                self.diff_actions[1] == ('+', self.new_value))

    @property
    def is_new(self):
        """Whether the current instance represents the definition of a new
        variable.
        """
        return len(self.diff_actions) == 1 and not self.old_value and \
            self.kind == VariableDifferenceKind.ADDED

    @property
    def is_unset(self):
        """Whether the current instance represents the removal/unsetting of
        an existing variable.
        """
        return len(self.diff_actions) == 1 and not self.new_value and \
            self.kind == VariableDifferenceKind.REMOVED


class Environment:
    """Owns and manages the understanding of environment variables' state
    attached to a shell.

    `Environment` manages two "states", the :py:attr:`current_environment` and
    the :py:attr:`stamped_environment`.
    The *current* environment is usually instantiated from the environment of
    the shell Envprobe is running in, while the *stamped* environment is loaded
    from storage and lives between executions of an Envprobe operation.
    """
    def __init__(self, shell, env=None,
                 variable_type_heuristic=default_heuristic):
        """Create an environment manager.

        Parameters
        ----------
        shell : .shell.Shell
            The shell to attach the manager to.
            The :py:attr:`.shell.Shell.configuration_directory` of the shell
            will be respected as data storage.
        env : dict, optional
            The raw mapping of environment variables to their values, as in
            :py:data:`os.environ`.
        variable_type_heuristic : HeuristicStack, optional
            The variable-to-:py:class:`.vartypes.EnvVar` type mapping
            heuristics.
            If not specified, :py:data:`default_heuristic` is used.
        """
        self._shell = shell
        self._current_environment = dict(deepcopy(env))
        self._stamped_environment = None
        self.type_heuristics = variable_type_heuristic

    def load(self):
        """Load the shell's saved environment from storage to
        :py:attr:`stamped_environment`.

        Note
        ----
        If there is no backing file associated with the current shell's state,
        or an IO error happens, the stamped environment will be loaded as
        empty.
        """
        if not (self._shell.is_envprobe_capable and
                self._shell.manages_environment_variables):
            self._stamped_environment = dict()
            return

        try:
            with open(self._shell.state_file, 'rb') as f:
                self._stamped_environment = pickle.load(f)  # nosec: pickle
        except OSError:
            self._stamped_environment = dict()

    def stamp(self):
        """Stamp the :py:attr:`current_environment`, making it become the
        :py:attr:`stamped_environment`.
        """
        self._stamped_environment = deepcopy(self._current_environment)

    def save(self):
        """Save the :py:attr:`stamped_environment` to the persistent storage.

        Note
        ----
        If there is no backing file associated with the current shell's state,
        the method will do nothing.
        """
        if not (self._shell.is_envprobe_capable and
                self._shell.manages_environment_variables):
            return

        with open(self._shell.state_file, 'wb') as f:
            pickle.dump(self._stamped_environment, f)
        os.chmod(self._shell.state_file, 0o0600)

    @property
    def current_environment(self):
        """Obtain the *current* environment, which is usually the state of
        variables the object was instantiated with.
        This is considered the "dirty state" of the environment the tool is
        running in.
        """
        return self._current_environment

    @property
    def stamped_environment(self):
        """Obtain the *stamped* environment which which is usually the one
        loaded from inter-session storage.
        This is considered the "pristine state" of the environment the tool is
        running in.
        """
        if self._stamped_environment is None:
            self.load()
        return self._stamped_environment

    def get_stamped_variable(self, variable_name):
        """Retrieve a :py:class:`.vartypes.EnvVar` environment variable from
        the :py:attr:`stamped_environment`'s values.

        Returns
        -------
        env_var : .vartypes.EnvVar
            The typed environment variable object.
            This object is always constructed, if there is no value associated
            with it then to a default empty state.
        is_defined : bool
            ``True`` if the variable was actually **defined** in the
            environment.
        """
        return create_environment_variable(variable_name,
                                           self.stamped_environment,
                                           self.type_heuristics), \
            variable_name in self.stamped_environment

    def __getitem__(self, variable_name):
        """Retrieve a :py:class:`.vartypes.EnvVar` environment variable from
        the :py:attr:`current_environment`'s values.

        Returns
        -------
        env_var : .vartypes.EnvVar
            The typed environment variable object.
            This object is always constructed, if there is no value associated
            with it then to a default empty state.
        is_defined : bool
            ``True`` if the variable was actually **defined** in the
            environment.
        """
        return create_environment_variable(variable_name,
                                           self.current_environment,
                                           self.type_heuristics), \
            variable_name in self.current_environment

    def set_variable(self, variable, remove=False):
        """Sets the value of `variable` in the :py:attr:`current_environment`
        to the parameter, i.e. storing the change to the dirty state.

        Parameters
        ----------
        variable : .vartypes.EnvVar
            The variable which should be saved.
        remove : bool
            If ``True``, the `variable` will be removed from the environment,
            otherwise the new value is saved.

        Warning
        -------
        The application of the change only happens to the "knowledge" of the
        environment manager instance.
        This method does not attempt to guarantee in any way that the change of
        the value is respected by the underlying `shell`.

        See Also
        --------
        apply_change
        """
        if not remove:
            self._current_environment[variable.name] = variable.raw()
        else:
            try:
                del self._current_environment[variable.name]
            except KeyError:
                pass

    def apply_change(self, variable, remove=False):
        """Applies the changes in `variable` to the
        :py:attr:`stamped_environment`, i.e. modifying the pristine state.

        Parameters
        ----------
        variable : .vartypes.EnvVar
            The environment variable which value has been modified.
            (If the variable does not exist in the environment, it will be
            added with its current value.)
        remove : bool
            If ``True``, the `variable` will be removed from the environment,
            otherwise, the new value is saved.

        Warning
        -------
        The application of the change only happens to the "knowledge" of the
        environment manager instance.
        This method does not attempt to guarantee in any way that the change of
        the value is respected by the underlying `shell`.

        See Also
        --------
        set_variable

        Note
        ----
        The function does **not** change what is written to persistent storage,
        only what is in the memory of the interpreter.
        Please use :py:func:`save()` to emit changes to disk.
        """
        if self._stamped_environment is None:
            self.load()

        if not remove:
            self._stamped_environment[variable.name] = variable.raw()
        else:
            try:
                del self._stamped_environment[variable.name]
            except KeyError:
                pass

    def diff(self):
        """Generate the difference between :py:attr:`stamped_environment` and
        :py:attr:`current_environment`.

        Returns
        -------
        dict(str, VariableDifference)
            The difference for each variable that has been added, removed,
            or changed when the two environments are compared.

        Note
        ----
        While this method is closely related and under the hood using
        :py:meth:`.vartypes.EnvVar.diff` to calculate the difference, the
        semantics of what is considered "added", "removed", and "changed"
        differ substantially.
        """
        diff = dict()

        def __create_difference(kind, var_name):
            try:
                old_exists = var_name in self._stamped_environment
                old = create_environment_variable(var_name,
                                                  self.stamped_environment,
                                                  self.type_heuristics)

                new_exists = var_name in self._current_environment
                new = create_environment_variable(var_name,
                                                  self.current_environment,
                                                  self.type_heuristics)
            except KeyError:
                # Creating the environment variable instance failed because it
                # was deemed not to be managed. Ignore.
                return

            if old.value == new.value:
                return

            if old.value != new.value:
                diff[var_name] = VariableDifference(
                        kind,
                        var_name,
                        old.value,
                        new.value,
                        type(old).diff(
                            old if old_exists else None,
                            new if new_exists else None))

        def __handle_elements(kind, iterable):
            for e in iter(iterable):
                __create_difference(kind, e)

        __handle_elements(
                VariableDifferenceKind.ADDED,
                set(self.current_environment.keys()) -
                set(self.stamped_environment.keys()))
        __handle_elements(
                VariableDifferenceKind.REMOVED,
                set(self.stamped_environment.keys()) -
                set(self.current_environment.keys()))
        __handle_elements(
                VariableDifferenceKind.CHANGED,
                set(self.current_environment.keys()) &
                set(self.stamped_environment.keys()))

        return diff
