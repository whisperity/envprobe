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


class CommunityData:
    # TODO: This.
    def get_description(self, var_name):
        raise NotImplementedError("TODO.")
        return dict()
