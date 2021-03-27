.. _snapshots:

===============
Saved snapshots
===============

This page details the user-facing commands which deal with interactively accessing the saved snapshots for environment variables.
**Saved snapshots** allow interactively storing some values for environment variables with a name, and later loading these changes in another shell, resulting in the environment set up the same way.

A recurring theme in this section is the mention of *current values* versus the *saved state*:

  * **Current values** are the values for all environment variables when an Envprobe command started executing.
    This state is the same as if ``env`` was called in the shell.
  * The **saved state** is the knowledge about environment variables' values when Envprobe last saved or loaded a snapshot.

Initially, when Envprobe is loaded into a shell, the *current values* at the time of loading becomes the first *saved state* itself.


Difference of current environment (``diff``, ``%``)
===================================================

.. py:function:: diff(VARIABLE..., format="normal")

    .. note::

        This command is only available if Envprobe has been :ref:`hooked<install_hook>` in the current shell.

    Show the difference between the current values of environment variables and the last known saved state.
    (A saved state is updated when ``save`` or ``load`` is called.
    The initial saved state is generated when :ref:`Envprobe is loaded<config_hook>`.)

    :param VARIABLE: The names of environment variables to show the diff for.
                     If empty, all :ref:`tracked<snapshots_tracking>` variables which changed values are shown.
    :param format:   The output format to generate.

                     * ``-n``/``--normal``: Generate a human-readable output.
                       This is the default option.
                     * ``-u``/``--unified``: Generate a more *machine-readable* output akin to `unified diffs <http://gnu.org/software/diffutils/manual/html_node/Unified-Format.html>`_.

    :type format: choice

    :Possible invocations:
        - ``ep diff [VARIABLE]``
        - ``ep % [VARIABLE]``

    :Examples:
        .. code-block:: bash

            $ ep PATH
            PATH=/foo:/bar
            $ ep FOO
            FOO is not defined
            $ ep NUM
            NUM=8

            $ ep +PATH /mnt
            $ ep -PATH /bar
            $ ep FOO=Bar
            $ ep ^NUM

            $ ep %
            (+) Added:       FOO
                    defined value: Bar

            (-) Removed:     NUM
                    value was:     8

            (!) Changed:     PATH
                    added:         /mnt
                    removed:       /bar

        .. code-block:: diff
            :caption: *Unified diff* output format for the above code example, as if ``ep % -u`` (or ``ep diff --unified``) was called.

            --- /dev/null
            +++ FOO
            @@ -0,0 +1,1 @@
            +Bar

            --- NUM
            +++ /dev/null
            @@ -1,1 +0,0 @@
            -8

            --- PATH
            +++ PATH
            @@ -1,2 +1,2 @@
             /foo
            -/bar
            +/mnt


Save the values/changes to a snapshot (``save``, ``}``)
=======================================================

.. py:function:: save(SNAPSHOT, VARIABLE..., patch=False)

    .. note::

        This command is only available if Envprobe has been :ref:`hooked<install_hook>` in the current shell.

    Create or update a named snapshot which will contain the values of environment variables.

    :param SNAPSHOT: The name of the snapshot to create.
    :param VARIABLE: The names of the environment variables which values should be saved.
                     If empty, all :ref:`tracked<snapshots_tracking>` variables which changed values will be saved.
    :param patch:    If ``-p``/``--patch`` is specified, the user is asked about individual change interactively.
    :type patch:     bool

    :Possible invocations:
        - ``ep save [--patch] SNAPSHOT [VARIABLE]``
        - ``ep } SNAPSHOT [-p] [VARIABLE]``

    :Examples:
        .. code-block:: bash

            $ ep +PATH /root
            $ ep save rootpath PATH
            For variable 'PATH' the element '/root' was added.

            $ ep FOO=Bar
            $ ep } foobar -p
            New variable 'FOO' with value 'bar'.
            Save this change? (y/N) _


Load a snapshot (``load``, ``{``)
=================================

.. py:function:: load(SNAPSHOT, VARIABLE..., dry_run=False, patch=False)

    .. note::

        This command is only available if Envprobe has been :ref:`hooked<install_hook>` in the current shell.

    TODO: Text here.

    :param SNAPSHOT: The name of the snapshot to load from.
    :param VARIABLE: The names of the environment variables which values should be updated.
                     If empty, all :ref:`tracked<snapshots_tracking>` variables in the snapshot will be loaded.
    :param patch:    If ``-p``/``--patch`` is specified, the user is asked about individual change interactively.
    :type patch:     bool
    :param dry_run:  If ``-n``/``--dry-run`` is specified, only the would-be loaded changes are printed to the standard output, but no actual change is made to the variables.
    :type dry_run:   bool

    :Possible invocations:
        - ``ep load [--dry-run] [--patch] SNAPSHOT [VARIABLE]``
        - ``ep { SNAPSHOT [-n] [-p] [VARIABLE]``

    :Examples:
        .. code-block:: bash

            $ ep PATH
            PATH=/bin

            $ ep load rootpath PATH
            For variable 'PATH' the element '/root' will be added.

            $ ep PATH
            PATH=/root:/bin

            $ ep FOO
            FOO is not defined

            $ ep { foobar -n
            New variable 'FOO' will be created with value 'bar'.

            $ ep FOO
            FOO is not defined

            $ ep { foobar -p
            New variable 'FOO' will be created with value 'bar'.
            Load and apply this change? (y/N) _


.. _snapshots_tracking:

Variable tracking
=================

Saving certain environment variables (such as ``PWD``, ``SHLVL``, etc.) to a snapshot might not be beneficial.
The *tracking configuration* for variables can be used to toggle whether a particular variable (in the current shell, or globally for your user account) is useful to be saved, or not.
If a variable is *tracked*, changes to it are allowed to be saved and loaded from snapshots.
Otherwise, a variable is called *ignored*.
An *ignored* variable can still be :ref:`queried and modified<envvars>` through Envprobe for the current shell.

The tracking behaviour for any given variable is resolved in the following order:

 1. If the *local configuration* (for the current shell session) contains an explicit decision for the variable, that decision is used.
 2. If the *global configuration* (for your user account) contains an explicit decision for the variable, that decision is used.
 3. The local configuration's default setting is used.
 4. The global configuration's default setting is used.
 5. If there are no explicit nor default settings in either configuration files, the variables are *tracked*, by default.

The tracking of a variable can be changed by the :ref:`track<config_track>` configuration command.
