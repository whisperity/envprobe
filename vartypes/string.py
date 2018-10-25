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


register_type(StringEnvVar, 'string')
