"""
Envprobe: easy environment variable manager with saved states on a per-shell
basis.
"""
import os

from . import community_descriptions
from . import environment
from . import shell


def assemble_standard_type_heuristics_pipeline():
    p = environment.HeuristicStack()

    # By default everything is a string.
    p += environment.EnvVarTypeHeuristic()
    # If the value or the name feels numbery, make it a number
    p += environment.NumericalValueEnvVarHeuristic()
    p += environment.NumericalNameEnvVarHeuristic()
    # If the path feels numbery, make it a number
    p += environment.PathEnvVarHeuristic()
    # Community-sourced descriptions available to the user trump the rest.
    p += community_descriptions.CommunityTypeHeuristic()
    # But ignoring own variables and hidden stuff trumps some more.
    p += environment.EnvprobeEnvVarHeuristic()
    p += environment.HiddenEnvVarHeuristic()

    return p


standard_vartype_pipeline = assemble_standard_type_heuristics_pipeline()


def get_shell_and_env_always(env_dict=None):
    """
    :return: A :type:`Shell` and :type:`Environment` (in a tuple) for the
    given environment variable mapping (or `os.environ` if not given), even
    if the current situation does not allow for a meaningful working (e.g.
    no shell is configured from the user).
    """
    if not env_dict:
        env_dict = os.environ

    try:
        sh = shell.get_current_shell(env_dict)
    except KeyError:
        sh = shell.FakeShell()

    env = environment.Environment(sh, env_dict, standard_vartype_pipeline)

    return sh, env
