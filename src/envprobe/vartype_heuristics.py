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
from envprobe.environment import EnvVarTypeHeuristic, HeuristicStack


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


class PathNameEnvVarHeuristic(EnvVarTypeHeuristic):
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


class ConfigurationResolvedHeuristic(EnvVarTypeHeuristic):
    """Implements a heuristic that reads from a
    :py:class:`.settings.variable_information.VariableInformation`
    configuration manager, and resolves the type of the variable based on
    these settings contained therein.
    """
    def __init__(self, loader):
        """
        Parameters
        ----------
        loader : str -> object
            This function is called with the name of a variable and should
            return an object similar to
            :py:class:`.settings.variable_information.VariableInformation` in
            which the type can be looked up.
        """
        self.loader = loader

    def __call__(self, name, env=None):
        varinfo_manager = self.loader(name)
        if not varinfo_manager:
            return None
        varinfo = varinfo_manager[name]
        if not varinfo:
            return None

        return varinfo.get("type", None)


def assemble_standard_type_heuristics_pipeline(varcfg_user_loader,
                                               varcfg_description_loader):
    """Creates the standard :py:class:`.environment.HeuristicStack` pipeline
    that decides the type for an environment variable.

    This pipeline uses the :ref:`configuration of the user<config_set>` and
    the community first, and then the heuristics pre-implemented in Envprobe
    to deduce a *vartype* for an environment variable.

    Parameters
    ----------
    varcfg_user_loader : str -> object
        The function used for the :py:class:`.ConfigurationResolvedHeuristic`
        internally.
        This function is called with the name of a variable and should return
        an object similar to
        :py:class:`.settings.variable_information.VariableInformation` in which
        the type can be looked up.
    varcfg_description_loader : str -> object
        The function used for the :py:class:`.ConfigurationResolvedHeuristic`
        internally.
        This function is called with the name of a variable and should return
        an object similar to
        :py:class:`.settings.variable_information.VariableInformation` in which
        the type can be looked up.
    """
    p = HeuristicStack()
    # (This is a **stack**, the execution is bottom to top in the order of
    # adding heuristics!)

    # By default everything is a string, to conform with POSIX.
    p += EnvVarTypeHeuristic()

    # If the value or the name feels numbery, make it a number.
    p += NumericalValueEnvVarHeuristic()
    p += NumericalNameEnvVarHeuristic()

    # If the variable looks like a path, use path.
    p += PathNameEnvVarHeuristic()
    # TODO: Create a builtin heuristic like NumericalValue for PATH-like stuff?

    # If the built-in heuristics fail, try to use the description database.
    p += ConfigurationResolvedHeuristic(varcfg_description_loader)

    # The user's own configuration should be respected highly, though.
    p += ConfigurationResolvedHeuristic(varcfg_user_loader)

    # Ignoring critical variables is number one priority.
    p += EnvprobeEnvVarHeuristic()
    p += HiddenEnvVarHeuristic()

    return p
