"""
Module which contains the classes for array-like environmental variables.
"""

from . import EnvVar, register_type


class ArrayEnvVar(EnvVar):
    """
    Represents an environmental variable which
    """

    def __init__(self, name, env_string, separator):
        """
        Initialize a new array environment variable where the given `separator`
        character acts as a separator. The inner array holds values as strings.
        """
        super().__init__(name, env_string)
        self._separator = separator
        self.value = env_string

    @property
    def separator(self):
        return self._separator

    @property
    def value(self):
        """
        Get the values in the environment variable as an array.

        You should NOT use this array directly to add or remove values from
        the variable.
        """
        return [self._transform_element_get(e) for e in self._value]

    @value.setter
    def value(self, new_value):
        """
        Set the value of the environment variable to the given array,
        or a string separated by the `separator` given to :func:`__init__`.
        This will automatically overwrite ALL the values stored within the
        array.
        """

        if isinstance(new_value, list):
            self._value = [self._transform_element_set(e) for e in new_value]
        elif isinstance(new_value, str):
            self._value = [self._transform_element_set(e)
                           for e in new_value.split(self.separator)]
        else:
            raise ValueError("Cannot set value of ArrayEnvVar to a non-list, "
                             "non-string parameter.")

    def _check_if_element_valid(self, elem):
        if self.separator in elem:
            # Disallow adding an element to the array which contains the
            # separator character. While escaping, e.g. ':' in PATH with '\:'
            # sounds like a good decision, currently no mainstream Linux or
            # macOS system supports an escaped letter in the PATH.
            # See: https://stackoverflow.com/a/29213487
            raise ValueError("Value to be added ('{0}') contains the "
                             "array-like environment variable's separator "
                             "character '{1}'. This will make the "
                             "environment variable unusable, as the "
                             "POSIX standard disallows this behaviour!"
                             .format(elem, self.separator))

        return True

    def _transform_element_get(self, elem):
        """
        Transform an element from the internal value in the array to the
        "external" (shell) representation before returning it to the client
        code.

        This should be the inverse method of :func:`_transform_element_set`.
        """
        return elem

    def _transform_element_set(self, elem):
        """
        Transform an element from the "external" value to the internal
        representation before setting it in the array.

        There should be no expectations by this method that the values given
        to the method are in any way proper.

        This should be the inverse method of :func:`_transform_element_get`.
        """
        return str(elem)

    def __getitem__(self, idx):
        """
        Subscript operator that returns the element with index `idx` in the
        environmental variable.
        """
        return self._transform_element_get(self._value[idx])

    def __setitem__(self, idx, elem):
        """
        Subscript setter operator that sets the given `idx`th element to
        `value`. The index must be an integer.
        """
        if self._check_if_element_valid(elem):
            elem = self._transform_element_set(elem)
            self._value[idx] = elem

    def __delitem__(self, idx):
        """
        Removes the element at index `idx` from the elements in the
        environmental variable.
        """
        del self._value[idx]

    def insert_at(self, idx, elem):
        """
        Insert a new value into the array at the position specified by `idx`.
        The elements to the right (having a larger index) will be shifted by
        one to make place for the new element.
        """
        if self._check_if_element_valid(elem):
            elem = self._transform_element_set(elem)
            self._value.insert(idx, elem)

    def remove_value(self, elem):
        """
        Removes ALL occurrence the given element from the array.
        """
        for _ in range(0, self._value.count(elem)):
            self._value.remove(elem)

    def to_raw_var(self):
        return self.separator.join(self._value).strip(self.separator)


class ColonSeparatedArrayEnvVar(ArrayEnvVar):
    """
    Represents an environmental variable in which array elements are
    separated by `:`.
    """

    def __init__(self, name, env_string):
        super().__init__(name, env_string, ':')


class SemicolonSeparatedArrayEnvVar(ArrayEnvVar):
    """
    Represents an environmental variable in which array elements are
    separated by `;`.
    """

    def __init__(self, name, env_string):
        super().__init__(name, env_string, ';')


register_type('colon-separated', ColonSeparatedArrayEnvVar)
register_type('semi-separated', SemicolonSeparatedArrayEnvVar)
