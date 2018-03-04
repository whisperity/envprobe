from . import EnvVar, register_type


class StringEnvVar(EnvVar):
    """
    The most basic environmental variable type which is a raw string
    contained in a variable.
    """

    def __init__(self, name, env_string):
        super().__init__(name, env_string)
        self.value = env_string

    @property
    def value(self):
        """
        Get the current value of the string environment variable.
        """
        return self._value

    @value.setter
    def value(self, new_value):
        """
        Set the value of the environment variable. `new_value` should be a
        string. If it is not, the `str()` conversion method is used.
        """
        if not isinstance(new_value, str):
            new_value = str(new_value)

        self._value = new_value

    def to_raw_var(self):
        return self.value


register_type(StringEnvVar, 'string')
