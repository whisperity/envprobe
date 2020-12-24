from .envvar import EnvVar, register_type


class Numeric(EnvVar):
    """This type may only hold a numeric (`int` or `float`) value.
    """

    def __init__(self, name, raw_value):
        """Create a new `Numeric` variable by converting `raw_value`."""
        super().__init__(name, raw_value)
        self.value = raw_value

    @classmethod
    def type_description(cld):
        """Contains a value that must be an integer or floating-point number.
        """
        return "Contains a value that must be an integer or floating-point " \
               "number."

    @property
    def value(self):
        """Get the value of the variable.

        Returns
        -------
        int or float
            The value.
        """
        return self._value

    @value.setter
    def value(self, new_value):
        """Sets the `value` to `new_value`.

        Parameters
        ----------
        new_value: int or float
            The new value.

        Raises
        ------
        ValueError
            If the given value is neither `int` nor `float`.
        """
        # First, try to make the variable a float. Every int can be a float
        # implicitly.
        try:
            self._value = float(new_value)
            self._kind = float
        except ValueError:
            raise

        if self._value.is_integer():
            # If the float is actually an integer, cast to integer.
            self._value = int(self._value)
            self._kind = int

    @property
    def is_integer(self):
        """Whether the value is of `int` type."""
        return self._kind == int

    @property
    def is_floating(self):
        """Whether the value is of `float` type."""
        return self._kind == float

    def raw(self):
        """Convert the value to raw shell representation, i.e. a string."""
        return str(self.value)

    @classmethod
    def get_difference(cls, old_variable, new_variable):
        if type(old_variable) != type(new_variable):
            raise TypeError("Only variables of the same type can be "
                            "differentiated.")

        ret = {'type': type(old_variable).__name__,
               'diff': []}
        if old_variable.value == new_variable.value:
            return ret

        ret['diff'].append(('+', str(new_variable.value)))
        ret['diff'].append(('-', str(old_variable.value)))
        return ret


register_type('numeric', Numeric)
