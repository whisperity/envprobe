Release notes for Envprobe `v1.0`
=================================

> :bulb: **Note!** Normally, the commit history between two releases should suffice as the release notes, but this major rewrite is so huge we need this extra bit to keep track.

New features and enhancements :newspaper:
-----------------------------------------

 * There's a shorter and more concise [README](/README.md), and a better and longer full [Documentation](/docs/index.rst) available.
 * *Envprobe* is now designed with offering most of the low-level functionality as a Python library, with the user-facing commands simply bolted on top.
   The internal details have been highly refactored and better documented.
 * There is now an automated CI system and testing! (#8)
 * Envprobe will now use the most temporary location possible to store the temporary files needed for operation, and will try its best to clean up after itself. (#11)


Bug fixes and performance improvements :beetle:
-----------------------------------------------

 * Fixed an issue with invalid control code generation when a variable's value contained spaces (#12).
 * Fixed saving changes to a PATH-like variable and then saving some more changes to it destroying the original saved values (#2).
 * Fixed the issue with saving or loading a snapshot resulted in the entire environment considered "stamped" (i.e. no more diffs between the current state and the known state), as opposed to only the changes that affected the variables actually saved or loaded. (#14)
 * Improved the handling of the control file to be done in Python, breaking our reliance on `/bin/cat` and `/bin/rm` (i.e. `/bin` being in `PATH`) being available. (#15)


Backwards incompatible and other game-breaking changes :warning:
----------------------------------------------------------------

 * The `envprobe.py` and `envprobe-config.py` entry point scripts have been **removed** and the shell hook made shorter and simpler. (#10)
   Now, the `envprobe` is the **only** entry point through which the program can be called.
 * The `epc track` and `epc default-tracking` commands have been merged together into the `epc track` command.
   Setting the *default behaviour* (previously through `epc default-tracking`) is done by giving the `--default` flag.
   Resetting a particular variable's behaviour to the default (previously done by `epc track --default`) is done by using `epc track --reset`.
 * The `epc set-type` and `epc set-description` commands have been merged together into the `epc set` command.
   The individual properties of the variable to be set can be specified with `--type` and `--description`, respectively.
 * Envprobe's user-level configuration files have been moved to `~/.config/envprobe` by default.
 * The internals of the implementation have been almost completely reworked, which means everything that relied upon Envprobe on the Python scripting level is surely broken!
 * The format of the user configuration files have changed in an incompatible way, too.
