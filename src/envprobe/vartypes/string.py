from .envvar import EnvVar, register_type


class String(EnvVar):
    """The standard type of environment variables."""

    def __init__(self, name, raw_value):
        """Create a new :py:class:`String` variable."""
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
        """Sets the :py:attr:`value` to `new_value`.

        Parameters
        ----------
        new_value : str
            The value to write.

            If `new_value` isn't a :py:class:`str`, it will be stringified
            automatically.
        """
        if not isinstance(new_value, str):
            new_value = str(new_value)
        self._value = new_value

    def raw(self):
        """Convert the value to raw shell representation.

        For :py:class:`String`s, this is equivalent to calling
        :py:attr:`value`.
        """
        return self.value


register_type('string', String)
