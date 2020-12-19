"""
Envprobe: easy environment variable manager with saved states on a per-shell
basis.
"""
import sys

from . import community_descriptions
from . import environment


print("Dummy: envprobe top-level file was imported.", file=sys.stderr)


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


STANDARD_PIPELINE = assemble_standard_type_heuristics_pipeline()
