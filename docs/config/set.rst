.. _config_set:

======================================================
Setting additional information for variables (``set``)
======================================================

.. py:function:: set(VARIABLE, description=None)
    :noindex:

    Set or change the additional information stored for a variable.

    :param VARIABLE: The name of the environment variable to alter, e.g. ``PATH``.

    :param description: Sets the user-friendly description of the variable to the given argment
                        This is a **cosmetic** or **informational** argument, and changes to it does not affect behaviour.
    :type description: str

    :Possible invocations:
        - ``envprobe config set VARIABLE [options...]``
        - ``epc set VARIABLE [options...]``

    :Examples:
        .. code-block::
            :caption: Setting a "cosmetic" configuration option ``--description`` which is queried by other commands.

            $ ep get -i USER
            USER=envprobe-user
            Type: 'string'

            $ epc set USER --description "The user's name."
            Set description for 'USER'.

            $ ep get -i USER
            USER=envprobe-user
            Type: 'string'
            Description:
                    The user's name.
            Source: local

