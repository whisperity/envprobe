Release notes for Envprobe `v1.0`
=================================

> :bulb: **Note!** Normally, the commit history between two releases should suffice as the release notes, but this major rewrite is so huge we need this extra bit to keep track.

New features and enhancements :newspaper:
-----------------------------------------

 * There's a shorter and more concise README, and a better and longer full Documentation available.
 * *Envprobe* is now designed with offering most of the low-level functionality as a Python library, with the user-facing commands simply bolted on top.
   The internal details have been highly refactored and better documented.
 * There is now an automated CI system and testing! (#8)


Bug fixes and performance improvements :beetle:
-----------------------------------------------

 * Fixed an issue with invalid control code generation when a variable's value contained spaces (#12).


Backwards incompatible and other game-breaking changes :warn:
-------------------------------------------------------------

 * The `envprobe.py` and `envprobe-config.py` entry point scripts have been **removed** and the shell hook made shorter and simpler. (#10)
   Now, the `envprobe` is the **only** entry point through which the program can be called.
 * Envprobe's user-level configuration files have been moved to `~/.config/envprobe` by default.
 * The internals of the implementation have been almost completely reworked, which means everything that relied upon Envprobe on the Python scripting level is surely broken!