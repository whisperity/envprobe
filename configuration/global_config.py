"""
This module stores global variables that must be shared between all modules of
envprobe.

Please do not introduce a too large global state in this module.
Please do not add dependencies of other modules to this module because almost
all parts of envprobe refers this module.
"""

# This list contains the valid subcommands that exist. These are not mapped
# as "get VARIABLE" when used in the short format `envprobe VARIABLE`.
REGISTERED_COMMANDS = []
