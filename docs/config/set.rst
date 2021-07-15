.. _config_set:

======================================================
Setting additional information for variables (``set``)
======================================================

.. py:function:: set(VARIABLE, type=None, description=None)
    :noindex:

    Set or change the additional information stored for a variable.

    :param VARIABLE: The name of the environment variable to alter, e.g. ``PATH``.

    :param type: Sets the :ref:`type of the variable <impl_vartypes_implemented_list>` to the specified value.
                 To **delete** the setting, set it explicitly to *empty string* (``--type ""``).
                 This change **affects the behaviour** of the variable moving forward.
    :type type: choice selection

    :param description: Sets the user-friendly description of the variable to the given argment.
                        To **delete** the setting, set it explicitly to *empty string* (``--description ""``).
                        This is a **cosmetic** or **informational** argument, and changes to it does not affect behaviour.
    :type description: str

    :Possible invocations:
        - ``envprobe config set VARIABLE [options...]``
        - ``epc set VARIABLE [options...]``

    :Examples:
        .. code-block:: bash
            :caption: Setting a behaviour-affecting configuration option ``--type`` which changes how Envprobe handles a variable.

            $ ep get -i PATH
            PATH=/bin:/sbin
            PATH:
                    /bin
                    /sbin
            Type: 'path'

            $ epc set PATH --type string
            Set type for 'PATH'.

            $ ep get -i PATH
            PATH=/bin:/sbin
            Type: 'string'
            Source: local

        .. code-block:: bash
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
                    "The user's name."
            Source: local

    .. note::
        When both the :ref:`community description knowledge-base<community_descriptions>` and the user's local settings contain someting for a ``VARIABLE``, the local settings take priority.
