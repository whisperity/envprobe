.. _envvars:

==============================
Managing environment variables
==============================

This page details all the user-facing commands in the *main mode* which deal with reading and writing environment variables.
The changes to the variables are applied to the environment of the shell the command was executed in.

All commands are offered through *shortcuts* to ease access to the core functions.


Reading (``get``, ``?``)
========================

Read and print the value of the specified variable.


.. py:function:: get(VARIABLE, info=False)

   Read and print the value of the environment variable ``VARIABLE`` to the standard output in the format ``VARIABLE=value``.

   :param VARIABLE: The name of the environment variable to query.
   :param info: Whether to print additional information.
   :type info: ``True`` if ``-i`` or ``info`` is given

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

      - The individual elements of the variable in order if it is an :ref:`array variable<vartype_array>`, after the variable name repeated, one per line.
      - The :ref:`type<vartypes>` of the variable within Envprobe.
      - TODO: Community data.

.. hint::

   Community features are yet to be migrated to the new version.


.. [1] The shorthand format ``ep VARIABLE`` for ``ep get VARIABLE`` is available only if the given variable name (``"VARIABLE"``) is not "shadowed" by a subcommand name that is valid at the time the command is executed.
   E.g. if ``get`` is an environment variable defined in the shell, saying ``ep get`` will not be resolved as if the user said ``ep get get``, but instead, it will simply call ``ep get`` without a variable name, resulting in an error.
   As most environment variables are named in *SCREAMING_SNAKE_CASE*, this should not pose an issue except in the rarest of situations.
