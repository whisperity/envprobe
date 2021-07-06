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
"""
Core functions of the vartypes library, that deal with defining the base class
for environment variable type implementations, and the dynamic loading
infrastructure.
"""
from abc import ABCMeta, abstractmethod
import importlib
import os


__ENVTYPE_CLASSES_TO_NAMES = {}
__ENVTYPE_NAMES_TO_CLASSES = {}


class EnvVarExtendedInformation:
    """Implements a storage for the extended user-facing knowledge about a
    variable.
    """
    def __init__(self):
        self._type = None
        self._description = None
        self._source = None

    def apply(self, configuration):
        """Applies the persisted configuration on the current object.

        Parameters
        ----------
        configuration : dict
            The configuration mapping too apply.
            See
            :py:meth:`envprobe.settings.variable_information.VariableInformation.__getitem__`
            for the format generated.
        """
        if not configuration:
            return

        def _apply_one(key):
            if key in configuration:
                setattr(self, "_" + key, configuration[key])
        _apply_one("type")
        _apply_one("source")
        _apply_one("description")

    @property
    def type(self):
        """The type class identifier (kind) for the current variable."""
        return self._type

    @property
    def source(self):
        """The annotated source repository where the variable's information
        was obtained from.
        """
        return self._source

    @property
    def description(self):
        """The human description about the usage of the variable."""
        return self._description

    @description.setter
    def description(self, new_value):
        """Sets the `description` to the given parameter.

        Parameters
        ----------
        new_value : str
            The new `description` to use.
        """
        self._description = new_value


class EnvVar(metaclass=ABCMeta):
    """Base class for an environment variable type's implementation.

    Note
    ----
    The implementations of this class are responsible for handling the **type**
    of an environment variable.
    The classes are instantiated with a *given* value, and are detached from
    actual environment afterwards, i.e. a change in the environment will
    **NOT** be reflected by what is available from the instances.
    """

    @abstractmethod
    def __init__(self, name, raw_value):
        """
        Parameters
        ----------
        name : str
            The name of the environment variable.
        raw_value : str
            The stringified raw value of the environment variable, as present
            in the operating system.
        """
        self._name = name
        self._extended = EnvVarExtendedInformation()

    @property
    def name(self):
        """The name of the variable."""
        return self._name

    @property
    def extended_attributes(self):
        """Returns the object managing the extended attributes (user-facing
        knowledge) about the variable.

        Returns
        -------
        configuration : EnvVarExtendedInformation
        """
        return self._extended

    @classmethod
    def type_description(cls):
        """The description of the environment variable **type**."""
        return "(Abstract base class for environment variables.)"

    @abstractmethod
    def raw(self):
        """Convert the value of the variable to a raw shell representation."""
        pass

    @property
    @abstractmethod
    def value(self):
        """Retrieves the `value` of the environment variable.

        Returns
        -------
        unknown
            The value.
            The (Python) type of the returned value is specific to the
            subclass.
        """
        pass

    @value.setter
    @abstractmethod
    def value(self, new_value):
        """Sets the `value` to the given parameter.

        Parameters
        ----------
        new_value : unknown
            The new `value` to write.
            The exact type of the accepted variable depends on the subclass.
        """
        pass

    @classmethod
    def _diff(cls, old, new):
        """This method implements the :py:func:`diff` action and should be
        overridden in subclasses.
        """
        if old.value == new.value:
            return []
        if not old.value:
            return [('+', new.value)]
        if not new.value:
            return [('-', old.value)]
        return [('-', old.value), ('+', new.value)]

    @classmethod
    def diff(cls, old, new):
        """Generate an iterable difference "actions" between two variables.

        Parameters
        ----------
        old : EnvVar or None
            The "left" or "baseline" side of the diff.
        new : EnvVar or None
            The "right" or "new" side of the diff.

        Returns
        -------
        list(char, str)
            The differences between the two variables' values.

            The first element of the tuple, (`char`), is either ``+``, ``-``
            or ``=`` for **new/added**, **old/removed**, and **unchanged**,
            respectively.
            For each entry in the list, the second element (`str`) is the
            affected value itself.
            The description of the difference is **always** of type `str`.

            If either the `old` or the `new` did not contain a value,
            the respective side will be missing from the list.

            If the two variables are equal, an empty list is returned.

        Raises
        ------
        TypeError
            Only variables of the same type, and only subclasses of
            :py:class:`EnvVar` may be differentiated.

        Note
        ----
        The implementation for the actual calculating of the difference should
        be provided in the overridden method :py:meth:`_diff` in the
        subclasses.
        """
        if old is None:
            # If the old variable did not exist, only return the new side.
            diff = type(new)._diff(type(new)("__NONE__"), new)
            return list(filter(lambda da: da[0] == '+', diff))
        if new is None:
            # If the new variable doesn't exist, only return the removal of
            # the old.
            diff = type(old)._diff(old, type(old)("__NONE__"))
            return list(filter(lambda da: da[0] == '-', diff))

        if type(old) != type(new):
            raise TypeError("Only variables of the same type can be "
                            "differentiated.")
        if not isinstance(old, EnvVar) or \
                not isinstance(new, EnvVar):
            raise TypeError("Only variables of 'EnvVar' can be "
                            "differentiated.")

        return type(old)._diff(old, new)

    def apply_diff(self, diff):
        """Applies the given difference to the value of the instance.

        Parameters
        ----------
        diff : list(char, str)
            A difference action list, as returned by :py:meth:`EnvVar.diff`.

        Raises
        ------
        ValueError
            If the diff is invalid or non-applicable.

        Note
        ----
        In most cases, the ``-`` (*remove*) side of the diff is ignored when
        applying.
        """
        positive_actions = list(filter(lambda d: d[0] == '+', diff))
        if len(positive_actions) != 1:
            raise ValueError("Bad diff: none or multiple '+' actions found!")

        self.value = positive_actions[0][1]

    @classmethod
    def merge_diff(cls, diff_a, diff_b):
        """Creates a merged diff from two diffs that simulates the transitive
        application of the first and the second diff in order.

        Parameters
        ----------
        diff_a : list(char, str)
            The difference actions to apply first, as returned by
            :py:meth:`EnvVar.diff`.
        diff_b : list(char, str)
            The difference actions to apply second, in the same format.

        Returns
        -------
        list(char, str)
            The merged difference actions' list. The format is kept.

        Raises
        ------
        ValueError
            If the diff is invalid or non-applicable.
        """
        positive_actions_a = list(filter(lambda d: d[0] == '+', diff_a))
        positive_actions_b = list(filter(lambda d: d[0] == '+', diff_b))

        if len(positive_actions_a) > 1:
            raise ValueError("Bad diff: multiple '+' actions in 'diff_a'!")
        if len(positive_actions_b) > 1:
            raise ValueError("Bad diff: multiple '+' actions in 'diff_b'!")

        if positive_actions_b:
            return positive_actions_b
        else:
            return positive_actions_a


def register_type(kind, clazz):
    """Register the :py:class:`EnvVar` implementation to the dynamic lookup
    mechanism.

    Parameters
    ----------
    kind : str
        The name of the environment variable type implementation.
    clazz : class
        The Python class that implements the functions.

    Raises
    ------
    TypeError
        `clazz` must be a type that is a subclass of :py:class:`EnvVar`,
        otherwise an exception is raised.

    Example
    -------
    The implementing modules of :py:class:`EnvVar` subclasses should be named
    similarly as the shell they are implementing, and after defining the
    ``class``, in the global code of the module itself, a call to
    :py:func:`register_type` should be present:

    .. code-block:: py
        :caption: Registering a hypothetical implementation of the Circle in
            ``envprobe.vartypes.circle``

        from envprobe.vartypes.envvar import EnvVar, register_type

        class Circle(EnvVar):
            # ... the implementation of the class ...

        register_type('circle', Circle)
    """
    if not issubclass(clazz, EnvVar):
        raise TypeError("{0} is not an EnvVar".format(str(clazz)))
    __ENVTYPE_CLASSES_TO_NAMES[clazz] = kind
    __ENVTYPE_NAMES_TO_CLASSES[kind] = clazz


def get_class(kind):
    """Retrieves the implementation class for the given name from the dynamic
    registry.

    Parameters
    ----------
    kind : str
        The name of the environment variable type, as registered.

    Returns
    -------
    class
        The class implementation.

    Raises
    ------
    KeyError
        Raised if the given `kind` is not registered.
    """
    return __ENVTYPE_NAMES_TO_CLASSES[kind]


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
    return __ENVTYPE_CLASSES_TO_NAMES[clazz]


def get_known_kinds():
    """Get the list of dynamically registered and loaded :py:class:`EnvVar`
    implementations.

    Returns
    -------
    list(str)
        The names.
    """
    return __ENVTYPE_NAMES_TO_CLASSES.keys()


def load(kind):
    """Attempt to load an :py:class:`EnvVar` implementation.

    The function loads the module `kind` from :py:mod:`envprobe.vartypes` and
    expects it to register the :py:class:`EnvVar` named `kind`.

    Parameters
    ----------
    kind : str
        The name of the environment variable type to load.
        The loading will be done from the similarly named Python module under
        :py:mod:`envprobe.vartypes`.

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
        Raised if the module successfully loaded, but there were no
        implementation with the name `kind` registered by it.
    """
    try:
        return get_class(kind)
    except KeyError:
        pass

    try:
        importlib.import_module("envprobe.vartypes.{0}".format(kind))
    except ModuleNotFoundError:
        raise

    try:
        # The loading of the module SHOULD register the type.
        return get_class(kind)
    except KeyError:
        raise NotImplementedError(
            "envprobe.vartypes.{0} did not register '{0}'".format(kind))


def load_all():
    """Loads all :py:class:`EnvVar` implementations to the interpreter found
    under :py:mod:`envprobe.vartypes` in the install.

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
