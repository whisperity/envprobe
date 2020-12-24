from .envvar import EnvVar


class Array(EnvVar):
    """An environment variable where elements are separated by a `separator`.
    """

    def __init__(self, name, raw_value, separator):
        """Create a new array with the given `separator`.
        Initialize a new array environment variable where the given `separator`
        character acts as a separator. The inner array holds values as strings.
        """
        super().__init__(name, raw_value)
        self._separator = separator
        self.value = raw_value

    @classmethod
    def type_description(cls):
        """An array of string elements separated by a separator."""
        return "An array of string elements separated by a separator."

    @property
    def separator(self):
        """Get the `separator` the object was instantiated with."""
        return self._separator

    @property
    def value(self):
        """Get the copy of the value of the variable, as a `list`.

        Returns
        -------
        list(str)
            The elements.

        Note
        ----
        You should **not** directly change the elements in this `list`, as the
        changes will not be reflected by the `Array` object.
        """
        return [self._transform_element_get(e) for e in self._value]

    @value.setter
    def value(self, new_value):
        """Set the value of the whole array to `new_value`.

        Parameters
        ----------
        new_value : list(str)
            The new array, if `new_value` is a `list`.
        new_value : str
            Create an array (using `separator`) from `new_value` if `new_value`
            is a `str`.

        Raises
        ------
        TypeError
            Raised if `new_value` is neither a `str` nor a `list`.
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
            raise TypeError("Cannot set value of ArrayEnvVar to a non-list, "
                            "non-string parameter.")

    def _check_if_element_valid(self, elem):
        """Check if the given `elem` contains the `separator` character.
        This is disallowed as per the POSIX standard (even if escaped)."""
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
        """Transform the given element from the internal representation to
        the external (shell) representation before giving it to the client.
        """
        return elem

    def _transform_element_set(self, elem):
        """Transform the given element from the raw external (shell)
        representation to the internal one before adding it to the array.
        """
        return str(elem)

    def __getitem__(self, idx):
        """Retrieve the in the array at `idx` index."""
        return self._transform_element_get(self._value[idx])

    def __setitem__(self, idx, elem):
        """Set the element in the array at `idx` to `elem`."""
        elem = self._transform_element_set(elem)
        if self._check_if_element_valid(elem):
            self._value[idx] = elem

    def __delitem__(self, idx):
        """Delete the element at index `idx`."""
        del self._value[idx]

    def __len__(self):
        """The length of the array."""
        return len(self._value)

    def insert_at(self, idx, elem):
        """Insert the element at a given index.

        Elements at or after `idx` currently in the array will be shifted to
        the right by 1.

        Parameters
        ----------
        idx : int
            The index to insert at.
            The new element will be at this index after insertion.
        elem : str
            The element to insert.
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
        """Removes all occurrences of `elem` from the array."""
        elem = self._transform_element_set(elem)
        for _ in range(0, self._value.count(elem)):
            self._value.remove(elem)

    def raw(self):
        """Convert the value to raw shell representation, i.e. a string
        separated by `separator`."""
        return self.separator.join(self._value).strip(self.separator)

    @classmethod
    def _diff(cls, old, new):
        """Generate a difference between `old` and `new` values.

        For `Array` variables, the elements that are same in both `old` and
        `new` will be emitted with an ``=`` ("unchanged") side.
        """
        def __deduplicate_list_keep_order(list):
            seen = set()
            return [x for x in list
                    if not (x in seen or seen.add(x))]

        old = __deduplicate_list_keep_order(old.value)
        new = __deduplicate_list_keep_order(new.value)
        if old == new:
            return []

        ret = []
        added = list(filter(lambda e: e not in old and e != '', new))
        removed = list(filter(lambda e: e not in new and e != '', old))
        kept = list(filter(lambda e: e in old and e in new and e != '',
                           __deduplicate_list_keep_order(old + new)))

        for add in added:
            ret.append(('+', add))
        for remove in removed:
            ret.append(('-', remove))
        for keep in kept:
            ret.append(('=', keep))

        return ret
