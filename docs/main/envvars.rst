.. _envvars:

==============================
Managing environment variables
==============================

This page details all the user-facing commands in the *main mode* which deal with reading and writing environment variables.
The changes to the variables are applied to the environment of the shell the command was executed in.

All commands are offered through *shortcuts* to ease access to the core functions.

.. note::

    These commands are only available if Envprobe has been :ref:`hooked<install_hook>` in the current shell.

.. _envvars_get:

Reading (``get``, ``?``)
========================

.. py:function:: get(VARIABLE, info=False)
    :noindex:

    Read and print the value of the environment variable ``VARIABLE`` to the standard output in the format ``VARIABLE=value``.

    :param VARIABLE: The name of the environment variable to query.
    :param info:     Whether to print additional information.
    :type info:      ``True`` if ``-i`` or ``info`` is given

    :Possible invocations:
        - ``ep get [-i|--info] VARIABLE``
        - ``ep ?VARIABLE``
        - ``ep VARIABLE`` [1]_

    :Examples:
       .. code-block:: bash

           $ ep PATH
           PATH=/usr/local/bin:/usr/bin:/sbin:/bin

       .. code-block:: bash

           $ ep get -i PATH
           PATH=/usr/local/bin:/usr/bin:/sbin:/bin

           PATH=
                 /usr/local/bin
                 /usr/bin
                 /sbin
                 /bin

           Type: 'path'

    *Priting additional information*:
        If ``-i``/``--info`` is given, additional information about the variable will be printed after the initial print of the value.
        This additional information includes:

        - The individual elements of the variable in order if it is an *array variable* (:py:class:`Array<envprobe.vartypes.array.Array>`), after the variable name repeated, one per line.
        - The :ref:`type class<impl_vartypes>` of the variable within Envprobe.
        - Additional stored information such as a *description* of the variable, based on the :ref:`stored configuration<config_set>` or the :ref:`downloaded community knowledge-base<community_descriptions>`.

.. [1] The shorthand format ``ep VARIABLE`` for ``ep get VARIABLE`` is available only if the given variable name (``"VARIABLE"``) is not "shadowed" by a subcommand name that is valid at the time the command is executed.
    E.g. if ``get`` is an environment variable defined in the shell, saying ``ep get`` will not be resolved as if the user said ``ep get get``, but instead, it will simply call ``ep get`` without a variable name, resulting in an error.
    As most environment variables are named in *SCREAMING_SNAKE_CASE*, this should not pose an issue except in the rarest of situations.


Writing (``set``, ``!``, ``=``)
===============================

.. py:function:: set(VARIABLE, VALUE)
    :noindex:

    Set the value of ``VARIABLE`` to the specified ``VALUE``.

    :param VARIABLE: The name of the environment variable to set.
    :param VALUE:    The new value to set to.

    :Possible invocations:
        - ``ep set VARIABLE VALUE``
        - ``ep !VARIABLE VALUE``
        - ``ep VARIABLE=VALUE``

    :Examples:
        .. code-block:: bash

            $ echo $SOME_VARIABLE
            # No result, the variable is not set.

            $ ep set SOME_VARIABLE MyValue

            $ echo $SOME_VARIABLE
            MyValue

        .. code-block:: bash

            $ which ls
            /bin/ls

            $ ep PATH
            PATH=/usr/local/bin:/usr/bin:/sbin:/bin

            $ ep PATH="/tmp"

            $ which ls
            # No result.


Undefining (``undefine``, ``^``)
================================

.. py:function:: undefine(VARIABLE)
    :noindex:

    Undefine the ``VARIABLE``.

    In some cases, there can be subtle differences between a variable that is defined (but usually empty string), and variables that are *not defined* at all.
    However, in many cases, the two are equivalent.

    :param VARIABLE: The name of the environment variable to undefine.

    :Possible invocations:
        - ``ep undefine VARIABLE``
        - ``ep ^VARIABLE``

    :Examples:
        .. code-block:: bash

            $ echo $USER
            root

            $ ep undefine USER

            $ echo $SOME_VARIABLE
            # No result, the variable is not set.

        .. code-block:: bash

           $ echo $HOME/bin
           /home/user/bin

           $ ep ^HOME

           $ echo $HOME/bin
           /bin

.. _envvars_add:

Adding to arrays (``add``, ``+``)
=================================

Traditionally, extending a variable such as ``PATH`` with your current working directory required executing a lengthy sequence: ``export PATH="$(pwd):${PATH}"``.

.. py:function:: add(VARIABLE, VALUE..., position=0)
    :noindex:

    Add the given ``VALUE`` (or values, can be multiple) to the ``VARIABLE`` array.
    The values will be located starting at the given ``position`` index, while all subsequent elements will be shifted to the right (to higher indices).

    :param VARIABLE: The name of the environment variable to add to.
    :param VALUE:    The value(s) to add.
    :param position: The position where the added value(s) will be put to.
                     A *positive* position counts from the beginning of the array, while a *negative* position counts from the end.
                     ``0`` is the **first**, and ``-1`` is the **last** element's position.
    :type position:  int

    :Possible invocations:
        - ``ep add [--position] VARIABLE VALUE``
        - ``ep +VARIABLE VALUE`` (for ``position = 0``)
        - ``ep VARIABLE+ VALUE`` (for ``position = -1``)

    :Examples:
        .. code-block:: bash

            $ ep PATH
            PATH=/usr/local/bin:/usr/bin:/sbin:/bin
            $ fancy
            fancy: command not found!

            $ ep add --position 0 PATH /opt/fancy/bin
            $ fancy
            Fancy tool works!

            $ ep PATH
            PATH=/opt/fancy/bin:/usr/local/bin:/usr/bin:/sbin:/bin

        .. code-block:: bash
            :caption: Using ``--position`` to control where the values will be added to.
                Note the ``^1`` markers indicating what the individual variables' positions are understood as.

            $ ep SOME_ARRAY
            SOME_ARRAY=Foo:Bar:Baz
            #          ^0  ^1  ^2
            #          -3^ -2^ -1^

            $ ep add --position 1 SOME_ARRAY BLAH
            $ ep SOME_ARRAY
            SOME_ARRAY=Foo:BLAH:Bar:Baz
            #          ^0  ^1   ^2  ^3
            #          -4^ -3^  -2^ -1^

            $ ep add --position -2 SOME_ARRAY FIZZ
            $ ep SOME_ARRAY
            SOME_ARRAY=Foo:BLAH:FIZZ:Bar:Baz

        .. code-block:: bash

            $ ep PATH
            PATH=/usr/local/bin:/usr/bin:/sbin:/bin

            $ ep PATH+ /

            $ ep PATH
            PATH=/usr/local/bin:/usr/bin:/sbin:/bin:/

    .. note::
        The ``add`` command only works with environment variables that are :py:class:`Array<envprobe.vartypes.array.Array>`.
        In case Envprobe did not correctly resolve the type of the variable, :ref:`you can configure it yourself<config_set>`.

.. _envvars_remove:

Removing from arrays (``remove``, ``-``)
========================================

.. py:function:: remove(VARIABLE, VALUE...)
    :noindex:

    Remove **all occurrences** of ``VALUE`` (or values, can be multiple) from the ``VARIABLE`` array.

    :param VARIABLE: The name of the environment variable to remove from.
    :param VALUE:    The value(s) to remove.

    :Possible invocations:
        - ``ep remove VARIABLE VALUE``
        - ``ep -VARIABLE VALUE``

    :Examples:
        .. code-block:: bash

            $ ep PATH
            PATH=/opt/fancy/bin:/usr/local/bin:/usr/bin:/sbin:/bin
            $ fancy
            Fancy tool works!

            $ ep remove PATH /opt/fancy/bin
            $ fancy
            fancy: command not found!

            $ ep PATH
            PATH=/usr/local/bin:/usr/bin:/sbin:/bin

        .. code-block:: bash
            :caption: **All** occurrences are removed.
                The following array has ``/bin`` in it *7* times.

            $ ep PATH
            PATH=/bin:/bin:/bin:/usr/local/bin:/bin:/usr/bin:/sbin:/bin:/bin:/bin

            $ ep -PATH /bin

            $ ep PATH
            PATH=/usr/local/bin:/usr/bin:/sbin

    .. note::
        The ``remove`` command only works with environment variables that are :py:class:`Array<envprobe.vartypes.array.Array>`.
        In case Envprobe did not correctly resolve the type of the variable, :ref:`you can configure it yourself<config_set>`.
