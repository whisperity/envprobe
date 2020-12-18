"""
Module which contains the classes for array-like environment variables.
"""

from . import register_type
from .envvar import EnvVar


class Array(EnvVar):
    """
    Represents an environment variable which contains an array of values.
    In shells, such variables are often separated by a pre-defined separator
    character (:variable:`self._separator`). See subclasses of this class for
    what kinds of separations are available.
    """

    def __init__(self, name, env_string, separator):
        """
        Initialize a new array environment variable where the given `separator`
        character acts as a separator. The inner array holds values as strings.
        """
        super().__init__(name, env_string)
        self._separator = separator
        self.value = env_string

    @staticmethod
    def type_description():
        return "An array of string variables, separated by a well-defined " \
               "separator character."

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
            if not new_value:
                self._value = []
            else:
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
            # See: http://stackoverflow.com/a/29213487
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
        elem = self._transform_element_set(elem)
        if self._check_if_element_valid(elem):
            self._value[idx] = elem

    def __delitem__(self, idx):
        """
        Removes the element at index `idx` from the elements in the
        environmental variable.
        """
        del self._value[idx]

    def __len__(self):
        """
        :return: The length of the array.
        """
        return len(self._value)

    def insert_at(self, idx, elem):
        """
        Insert a new value into the array at the position specified by `idx`.
        The elements to the right (having a larger index) will be shifted by
        one to make place for the new element.
        """
        elem = self._transform_element_set(elem)
        if self._check_if_element_valid(elem):
            if idx >= 0:
                self._value.insert(idx, elem)
            elif idx < -1:
                # We cannot use list::insert here, because l[-1] = "a" is not
                # equal to list.insert(-1, "a"). The latter one actually
                # modifies the second-to-last element of the list, after
                # moving the last element to the right.

                # So instead, insert at the element right after the insertion
                # position, this way [1, 2].insert_at(-2, "a") will result in
                # [1, "a", 2]. This corresponds to the command-line help
                # "the element will be inserted AT the position given,
                # shifting every element AFTER the new one to the right".
                self._value.insert(idx + 1, elem)
            else:
                self._value.append(elem)

    def remove_value(self, elem):
        """
        Removes ALL occurrence the given element from the array.
        """
        elem = self._transform_element_set(elem)
        for _ in range(0, self._value.count(elem)):
            self._value.remove(elem)

    def to_raw_var(self):
        return self.separator.join(self._value).strip(self.separator)

    @classmethod
    def get_difference(cls, old_variable, new_variable):
        if type(old_variable) != type(new_variable):
            raise TypeError("Only variables of the same type can be "
                            "differentiated.")

        ret = {'type': type(old_variable).__name__,
               'diff': []}

        # The difference "actions" of arrays is a comparison of elements
        # from old to new.

        def __deduplicate_list_keep_order(list):
            seen = set()
            return [x for x in list
                    if not (x in seen or seen.add(x))]

        old = __deduplicate_list_keep_order(old_variable.value)
        new = __deduplicate_list_keep_order(new_variable.value)
        if old == new:
            return ret

        added = list(filter(lambda e: e not in old and e != '', new))
        removed = list(filter(lambda e: e not in new and e != '', old))
        kept = list(filter(lambda e: e in old and e in new and e != '',
                           __deduplicate_list_keep_order(old + new)))

        for add in added:
            ret['diff'].append(('+', add))
        for remove in removed:
            ret['diff'].append(('-', remove))
        for keep in kept:
            ret['diff'].append((' ', keep))

        return ret


class ColonSeparatedArray(Array):
    """
    Represents an environment variable in which array elements are
    separated by `:`.
    """

    def __init__(self, name, env_string):
        super().__init__(name, env_string, ':')

    @staticmethod
    def type_description():
        return "A list of string variables in an array, separated by :"


class SemicolonSeparatedArray(Array):
    """
    Represents an environment variable in which array elements are
    separated by `;`.
    """

    def __init__(self, name, env_string):
        super().__init__(name, env_string, ';')

    @staticmethod
    def type_description():
        return "A list of string variables in an array, separated by ;"


register_type('colon-separated', ColonSeparatedArray)
register_type('semi-separated', SemicolonSeparatedArray)
