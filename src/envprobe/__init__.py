"""Envprobe: Easy environment variable manager with saved states on a per-shell
basis.
"""
from . import community_descriptions
from . import environment
from . import main
from . import shell
from . import vartypes
from . import vartype_heuristics
from .library import get_shell_and_env_always

__all__ = ['community_descriptions',
           'environment',
           'main',
           'shell',
           'vartypes',
           'vartype_heuristics',
           'get_shell_and_env_always'
           ]
