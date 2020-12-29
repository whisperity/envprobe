import os

from .environment import Environment
from .shell import get_current_shell, FakeShell
from .vartype_heuristics import standard_vartype_pipeline


def get_shell_and_env_always(env_dict=None):
    """Return an :py:class:`environment.Environment` and
    :py:class:`shell.Shell`, no matter what.

    Parameters
    ----------
    env_dict : dict, optional
        The raw mapping of environment variables to their values, as in
        :py:data:`os.environ`.

    Return
    ------
    shell : .shell.Shell
        The shell which use can be deduced from the current environment (by
        calling :py:func:`.shell.get_current_shell`).
        If none such can be deduced, a :py:class:`.shell.FakeShell` is
        returned, which is a **valid** :py:class:`.shell.Shell` subclass that
        tells the client code it is not capable of anything.
    env : .environment.Environment
        The environment associated with the current context and the
        instantiated `Shell`.
    """
    if not env_dict:
        env_dict = os.environ

    try:
        sh = get_current_shell(env_dict)
    except KeyError:
        sh = FakeShell()

    env = Environment(sh, env_dict, standard_vartype_pipeline)

    return sh, env
