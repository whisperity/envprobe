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
from copy import deepcopy

from envprobe.compatibility import nullcontext


K_DEFAULT_SETTING = 'default'
K_TRACK_LIST = 'explicit_track'
K_IGNORE_LIST = 'explicit_ignore'


def get_tracking_file_name():
    """Returns the expected default name of the tracking configuration file.

    Warning
    -------
    This method only returns the **filename** for the configuration file,
    not its location or full path.
    """
    return "variable_tracking.json"


class VariableTracking:
    """Allows access to the user's configuration files about which variables
    are tracked.

    In most cases, the tracking is configured on two levels, a local (usually
    a shell's configuration) level, and a global (user's) level.
    The class's behaviour reflects the two configurations in an overlay, with
    the local settings trumping the global ones.
    """

    config_schema_global = {K_DEFAULT_SETTING: True,
                            K_TRACK_LIST: set(),
                            K_IGNORE_LIST: set()
                            }

    config_schema_local = {K_TRACK_LIST: set(),
                           K_IGNORE_LIST: set()
                           }

    def __init__(self, global_configuration=None, local_configuration=None):
        """Initialises the tracking manager.

        This instantiation is cheap.
        Access to the underlying data is only done when a query or setter
        function is called.

        Parameters
        ----------
        global_configuration : context-capable dict, optional
        local_configuration : context-capable dict, optional
        """
        self._global = global_configuration \
            if global_configuration is not None \
            else nullcontext(deepcopy(self.config_schema_global))
        self._local = local_configuration \
            if local_configuration is not None \
            else nullcontext(deepcopy(self.config_schema_local))

    @property
    def global_tracking(self):
        """Returns `True` if the default behaviour for tracking is `ON` in the
        **global** configuration.
        """
        with self._global as conf:
            return conf.get(K_DEFAULT_SETTING, True)

    @global_tracking.setter
    def global_tracking(self, new_value):
        """Sets the global tracking behaviour."""
        with self._global as conf:
            if new_value is None:
                del conf[K_DEFAULT_SETTING]
            else:
                conf[K_DEFAULT_SETTING] = bool(new_value)

    @property
    def local_tracking(self):
        """Returns `True` if the default behaviour for tracking is `ON` in the
        **local** configuration.
        """
        with self._local as conf:
            return conf.get(K_DEFAULT_SETTING, None)

    @local_tracking.setter
    def local_tracking(self, new_value):
        """Sets the local tracking behaviour."""
        with self._local as conf:
            if new_value is None:
                del conf[K_DEFAULT_SETTING]
            else:
                conf[K_DEFAULT_SETTING] = bool(new_value)

    @property
    def default_tracking(self):
        """Returns `True` if the current default tracking behaviour is `ON`."""
        local = self.local_tracking
        return local if local is not None else self.global_tracking

    def _unmark(self, variable_name, configuration):
        try:
            configuration[K_TRACK_LIST].remove(variable_name)
        except KeyError:
            pass
        try:
            configuration[K_IGNORE_LIST].remove(variable_name)
        except KeyError:
            pass

    def _tracked(self, variable_name, configuration):
        return variable_name in configuration[K_TRACK_LIST]

    def _ignored(self, variable_name, configuration):
        return variable_name in configuration[K_IGNORE_LIST]

    def _config(self, variable_name, configuration):
        return self._tracked(variable_name, configuration) or \
               self._ignored(variable_name, configuration)

    def _mark(self, variable_name, configuration, track):
        # A variable cannot be tracked and ignored at the same time.
        self._unmark(variable_name, configuration)

        key_to_add_to = K_TRACK_LIST if track else K_IGNORE_LIST
        configuration[key_to_add_to].add(variable_name)

    def track_local(self, variable_name):
        """Marks the variable to be tracked in the **local** scope."""
        with self._local as conf:
            self._mark(variable_name, conf, True)

    def is_tracked_local(self, variable_name):
        """Returns whether the variable is set to be tracked in the
        **local** configuration file.
        """
        with self._local as conf:
            return self._tracked(variable_name, conf)

    def ignore_local(self, variable_name):
        """Marks the variable to be ignored in the **local** scope."""
        with self._local as conf:
            self._mark(variable_name, conf, False)

    def unset_local(self, variable_name):
        """Removes the variable from the track or ignore lists in the **local**
        scope, making the default behaviour apply.
        """
        with self._local as conf:
            self._unmark(variable_name, conf)

    def track_global(self, variable_name):
        """Marks the variable to be tracked in the **global** scope."""
        with self._global as conf:
            self._mark(variable_name, conf, True)

    def is_tracked_global(self, variable_name):
        """Returns whether the variable is set to be tracked in the
        **global** configuration file.
        """
        with self._global as conf:
            return self._tracked(variable_name, conf)

    def ignore_global(self, variable_name):
        """Marks the variable to be ignored in the **global** scope."""
        with self._global as conf:
            self._mark(variable_name, conf, False)

    def unset_global(self, variable_name):
        """Removes the variable from the track or ignore lists in the
        **global** scope, making the default behaviour apply.
        """
        with self._global as conf:
            self._unmark(variable_name, conf)

    def is_explicitly_configured_local(self, variable_name):
        """Returns whether `variable_name` has an explicit track/ignore record
        in the **local** scope.
        """
        with self._local as conf:
            return self._config(variable_name, conf)

    def is_explicitly_configured_global(self, variable_name):
        """Returns whether `variable_name` has an explicit track/ignore record
        in the **global** scope.
        """
        with self._global as conf:
            return self._config(variable_name, conf)

    def is_tracked(self, *variables):
        """Resolves whether the `variable_name` are tracked according to the
        loaded configuration.

        The resolution order for the tracking status of a variable is the
        following:

            1. If the variable is explicitly tracked/ignored locally,
               the result.
            2. If the variable is explicitly tracked/ignored globally,
               the result.
            3. If there is a default tracking set locally, that value.
            4. The default global tracking setting.
            5. `True`, i.e. the variable is deemed tracked.

        Parameters
        ----------
        *variables: list(str) or str
            The list of variable names to check, either a single string, a
            variable length argument pass, or a list.

        Returns
        -------
        list(bool) or bool
            If only one element was given to `variables`, a single result is
            returned, which is ``True`` if the variable should be considered
            tracked, and ``False`` otherwise.
            If multiple names were passed, a list is returned, with each result
            being the result for the passed varaible, in order.
        """
        if not variables:
            raise AttributeError("variables")
        if len(variables) == 1 and isinstance(variables[0], list):
            # Fallback case if a single variable name is given as a list.
            variables = variables[0]

        with self._local as loc, self._global as glo:
            def _handle_single_variable(variable):
                # Explicit local track/ignore.
                if self._tracked(variable, loc):
                    return True
                elif self._ignored(variable, loc):
                    return False

                # Explicit global track/ignore.
                if self._tracked(variable, glo):
                    return True
                if self._ignored(variable, glo):
                    return False

                # Default local behaviour.
                local_def = loc.get("default", None)
                if local_def is not None:
                    return local_def

                # Default global behaviour.
                global_def = glo.get("default", None)
                if global_def is not None:
                    return global_def

                # Fallback to always track if nothing matched prior.
                return True

            results = list(map(_handle_single_variable, variables))

        if len(results) == 1:
            results = results[0]

        return results
