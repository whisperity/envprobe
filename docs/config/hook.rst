.. _config_hook:

==============================
Generating the hook (``hook``)
==============================

.. py:function:: hook(SHELL, PID)

    Print the shell script that is used to hook and set up Envprobe to the current shell.

    :param SHELL: The "type" identifier of the current shell.
                  This usually corresponds to the shell's name, such as ``bash`` or ``zsh``.
    :param PID:   The process ID ("pid") of the current shell.
                  This is commonly specified by letting the shell expand ``$$`` and passing the result.
    :type PID:    int

    :Possible invocations:
        - ``envprobe config hook SHELL PID`` [1]_

    :Examples:
        .. code-block:: bash

            $ ep
            ep: command not found!

            $ envprobe config hook bash $$
            # If Envprobe isn't registered already...
            if [[ ! "$PROMPT_COMMAND" =~ "__envprobe" ]]; then
                # ... multiple lines of Shell script follow ...
            fi

            $ ep
            ep: command not found!

            $ eval "$(envprobe config hook bash $$);"
            $ ep
            usage: envprobe [-h] ...

    .. hint ::

        The output of this command is not directly useful for any particular purpose other than to execute the resulting script (commonly by calling ``eval`` on it) in the context of a running shell.
        See :ref:`the install guide<install_hook>` on how to set up that all running shells are with Envprobe installed.

.. [1] While the shorthand ``epc`` is used for commands in the ``envprobe config`` mode (see :ref:`config mode<config>`), the ``hook`` command is special, as it is not available once a shell has been hooked.
     Thus, the full command must be typed out.
