"""Implement some certain compatibility features between Python versions."""

try:
    # nullcontext() is only available starting Python 3.7.
    from contextlib import nullcontext
except ImportError:
    class _ContextWrapper:
        def __init__(self, obj):
            self._obj = obj

        def __enter__(self):
            return self._obj

        def __exit__(self, *args):
            pass

    def nullcontext(enter_result=None):
        """Returns a context manager that returns `enter_result` from
        ``__enter__``, but otherwise does nothing.
        """
        return _ContextWrapper(enter_result)
