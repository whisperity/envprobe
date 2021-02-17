# Copyright (C) 2018 Whisperity
#
# SPDX-License-Identifier: GPL-3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from .community_descriptions import CommunityTypeHeuristic
from .environment import EnvVarTypeHeuristic, HeuristicStack


class EnvprobeEnvVarHeuristic(EnvVarTypeHeuristic):
    """Disable access to internal variables that begin with ``ENVPROBE_``."""
    def __call__(self, name, env=None):
        if name.startswith("ENVPROBE_"):
            return False


class HiddenEnvVarHeuristic(EnvVarTypeHeuristic):
    """Disable access to every variable that begins with ``_``, similar to how
    files named as such are considered "hidden"."""
    def __call__(self, name, env=None):
        if name.startswith('_'):
            return False


class PathEnvVarHeuristic(EnvVarTypeHeuristic):
    """Regard ``PATH`` and variables that end with ``_PATH`` as
    :py:class:`.vartypes.path.Path`.
    """
    def __call__(self, name, env=None):
        if name == "PATH" or name.endswith("_PATH"):
            return 'path'


class NumericalNameEnvVarHeuristic(EnvVarTypeHeuristic):
    """Regard commonly numeric-only variables as
    :py:class:`.vartypes.numeric.Numeric`.
    """
    def __call__(self, name, env=None):
        if name.endswith(("PID", "PORT")):
            return 'numeric'


class NumericalValueEnvVarHeuristic(EnvVarTypeHeuristic):
    """Regard environment variables that *currently* have a numeric value
    as :py:class:`.vartypes.numeric.Numeric`.
    """
    def __call__(self, name, env=None):
        if not env:
            return None

        value = env.get(name, "")
        try:
            float(value)
            return 'numeric'
        except ValueError:
            return None


def assemble_standard_type_heuristics_pipeline():
    p = HeuristicStack()

    # By default everything is a string.
    p += EnvVarTypeHeuristic()
    # If the value or the name feels numbery, make it a number
    p += NumericalValueEnvVarHeuristic()
    p += NumericalNameEnvVarHeuristic()
    # If the path feels numbery, make it a number
    p += PathEnvVarHeuristic()
    # Community-sourced descriptions available to the user trump the rest.
    p += CommunityTypeHeuristic()
    # But ignoring own variables and hidden stuff trumps some more.
    p += EnvprobeEnvVarHeuristic()
    p += HiddenEnvVarHeuristic()

    return p


standard_vartype_pipeline = assemble_standard_type_heuristics_pipeline()
"""The standard :py:class:`.environment.HeuristicStack` pipeline that decides
the type for an environment variable.

This pipeline uses the configuration of the user (TODO: make this a URL!) and
the community (TODO!) first, and then the heuristics pre-implemented in
Envprobe to deduce a *vartype* for an environment variable.

.. hint::

    **TODO:** Some of the features (such as user configuration or community
    data) are not implemented yet!
"""
