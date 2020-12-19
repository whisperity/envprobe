"""
This module implements the reader interface for the shared
"Environment Variable Descriptions" community project. This feature allows
fetching the necessary type and a usage description from a shared source.

The current canonical "community description" repository is accessible at:
    http://github.com/whisperity/Envprobe-Descriptions
"""
from .environment import EnvVarTypeHeuristic


class CommunityTypeHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        # TODO: Implement this module. So far, ignore the heuristic, as if
        #       never existed.
        return None
