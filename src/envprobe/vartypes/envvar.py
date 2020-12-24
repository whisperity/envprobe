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

    @property
    def name(self):
        """The name of the variable."""
        return self._name

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
        *unknown*
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
        new_value : *unknown*
            The new `value` to write.
            The exact type of the accepted variable depends on the subclass.
        """
        pass

    @classmethod
    def _diff(cls, old, new):
        """This method implements the `diff` action and should be overridden
        in subclasses.
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
        old : EnvVar
            The "left" or "baseline" side of the diff.
        new : EnvVar
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

            If either the `old` or the `new` did not contain a value,
            the respective side will be missing from the list.

            If the two variables are equal, an empty list is returned.

            The description of the difference is **always** of type `str`.

        Raises
        ------
        TypeError
            Only variables of the same type, and only subclasses of `EnvVar`
            may be differentiated.
        """
        if type(old) != type(new):
            raise TypeError("Only variables of the same type can be "
                            "differentiated.")
        if not isinstance(old, EnvVar) or \
                not isinstance(new, EnvVar):
            raise TypeError("Only variables of 'EnvVar' can be "
                            "differentiated.")

        return type(old)._diff(old, new)


def register_type(kind, clazz):
    """Register the `EnvVar` implementation to the dynamic lookup mechanism.

    Parameters
    ----------
    kind : str
        The name of the environment variable type implementation.
    clazz : class
        The Python class that implements the functions.

    Raises
    ------
    TypeError
        `clazz` must be a type that is a subclass of `EnvVar`, otherwise an
        exception is raised.

    Example
    -------
    The implementing modules of `EnvVar` subclasses should be named similarly
    as the shell they are implementing, and after defining the ``class``, in
    the global code of the module itself, a call to `register_type` should be
    present:

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

    Return
    ------
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

    Return
    ------
    str
        The registered name for the implementation.

    Raises
    ------
    KeyError
        Raised if the given `clazz` is not registered.
    """
    return __ENVTYPE_CLASSES_TO_NAMES[clazz]


def get_known_kinds():
    """Get the list of dynamically registered and loaded `EnvVar`
    implementations.

    Return
    ------
    list(str)
        The names.
    """
    return __ENVTYPE_NAMES_TO_CLASSES.keys()


def load(kind):
    """Attempt to load an `EnvVar` implementation.

    The function loads the module `kind` from ``envprobe.vartypes`` and
    expects it to register the `EnvVar` named `kind`.

    Parameters
    ----------
    kind : str
        The name of the environment variable type to load.
        The loading will be done from the similarly named Python module under
        `envprobe.vartypes`.

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
        importlib.import_module("envprobe.vartypes.%s" % kind)
    except ModuleNotFoundError:
        raise

    try:
        # The loading of the module SHOULD register the type.
        return get_class(kind)
    except KeyError:
        raise NotImplementedError(
            "envprobe.vartypes.{0} did not register '{0}'".format(kind))


def load_all():
    """Loads all `EnvVar` implementations to the interpreter found under
    `envprobe.vartypes` in the install.

    This method does not throw if a module does not actually register anything.
    """
    for f in os.listdir(os.path.dirname(__loader__.path)):
        try:
            load(f.split('.')[0])
        except NotImplementedError:
            pass
