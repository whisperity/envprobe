import pytest

from envprobe import vartypes


def test_invalid_type_fails_to_load():
    with pytest.raises(NotImplementedError):
        vartypes.load("false-type")
