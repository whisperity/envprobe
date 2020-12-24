from .envvar import EnvVar, register_type


class String(EnvVar):
    """The standard type of environment variables."""

    def __init__(self, name, raw_value):
        """Create a new `String` variable."""
        super().__init__(name, raw_value)
        self.value = raw_value

    @classmethod
    def type_description(cls):
        """The most basic environment variable, which contains
        type-nondescript strings as values."""
        return "The most basic environment variable which contains type-" \
               "nondescript strings as values."

    @property
    def value(self):
        """Get the value of the variable.

        Returns
        -------
        str
            The value.
        """
        return self._value

    @value.setter
    def value(self, new_value):
        """Sets the `value` to `new_value`.

        Parameters
        ----------
        new_value : str
            The value to write.
            If `new_value` isn't a `str`, it will be stringified automatically.
        """
        if not isinstance(new_value, str):
            new_value = str(new_value)
        self._value = new_value

    def raw(self):
        """Convert the value to raw shell representation.

        For `String`s, this is equivalent to calling `value`.
        """
        return self.value

    @classmethod
    def get_difference(cls, old_variable, new_variable):
        if type(old_variable) != type(new_variable):
            raise TypeError("Only variables of the same type can be "
                            "differentiated.")

        ret = {'type': type(old_variable).__name__,
               'diff': []}
        if old_variable.value == new_variable.value:
            return ret

        if new_variable.value != '':
            ret['diff'].append(('+', new_variable.value))
        if old_variable.value != '':
            ret['diff'].append(('-', old_variable.value))
        return ret


register_type('string', String)
