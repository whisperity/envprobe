.. _envvars:

==============================
Managing environment variables
==============================

This page details all the user-facing commands in the *main mode* which deal with reading and writing environment variables.
The changes to the variables are applied to the environment of the shell the command was executed in.

All commands are offered through *shortcuts* to ease access to the core functions.


Reading (``get``, ``?``)
========================

.. py:function:: get(VARIABLE, info=False)

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
      - TODO: Community data.

..
   TODO.
.. hint::

   Community features are yet to be migrated to the new version.

.. [1] The shorthand format ``ep VARIABLE`` for ``ep get VARIABLE`` is available only if the given variable name (``"VARIABLE"``) is not "shadowed" by a subcommand name that is valid at the time the command is executed.
   E.g. if ``get`` is an environment variable defined in the shell, saying ``ep get`` will not be resolved as if the user said ``ep get get``, but instead, it will simply call ``ep get`` without a variable name, resulting in an error.
   As most environment variables are named in *SCREAMING_SNAKE_CASE*, this should not pose an issue except in the rarest of situations.


Writing (``set``, ``!``, ``=``)
===============================

.. py:function:: set(VARIABLE, VALUE)

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
