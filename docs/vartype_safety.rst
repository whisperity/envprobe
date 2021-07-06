.. _vartype_safety:

================
Type-safe access
================

Conventionally, environment variables are stored as *strings* (character sequences, text) in the system.
A running program that uses the environment variable receives it as such a textual data, and in case the variable represents a number and the program wants to use it as a number, the program must perform the conversion.
This causes a problematic situation, as users are allowed to set any environment variable to any value, e.g. setting ``SSH_AGENT_PID`` (referring a service program's identifier, which is a number) to any unrelated, non-numeric, bad value.

**Envprobe** offers *type-safe* modification of environment variables.
This is achieved through a set of built-in *heuristics*, e.g. ``_PATH`` variables should be considered `pathlike` (``:``-separated arrays of directories), or ``_PID`` variables should be considered `numeric`.
(You can read more details about :ref:`the available types<impl_vartypes_implemented_list>`.)
In case you want to assign an invalid value considering the variable's type, an error is given instead.

.. code-block:: bash

    $ echo $SSH_AGENT_PID
    12345

    $ export SSH_AGENT_PID="invalid-value"
    # The above example works, even though a "_PID" variable should only
    # contain numbers.

    $ ep SSH_AGENT_PID=98765
    $ ep SSH_AGENT_PID="foo"
    [ERROR] Failed to execute: could not convert string to number.

    $ ep SSH_AGENT_PID
    SSH_AGENT_PID=98765

Certain operations, such as :ref:`adding<envvars_add>` and :ref:`removing<envvars_remove>` elements are only allowed on `Array` types.

.. code-block:: bash

    $ ep add USER foo
    [ERROR] Failed to execute: 'add' can not be called on non-arrays.

    $ ep add PATH /foo

    $ ep PATH
    PATH=/foo:/bin:/sbin

Apart from the built-in heuristics, you can **set the type of a variable** yourself with the :ref:`envprobe config set<config_set>` command.

.. code-block:: bash

    $ ep add USER foo
    [ERROR] Failed to execute: 'add' can not be called on non-arrays.

    $ epc set USER --type colon_separated   # Explicitly set "arr:ay".
    Set type for 'USER'.

    $ ep USER
    USER=envprobe-user

    $ ep add USER foo
    $ ep USER
    USER=foo:envprobe-user

    $ epc set USER --type ""                # Reset to default heuristic.
    $ ep USER
    USER="foo:envprobe-user"

    $ ep add USER foo
    [ERROR] Failed to execute: 'add' can not be called on non-arrays.

.. note::

    **TODO** Write about the Community project?
