.. _config_hook:

==============================
Generating the hook (``hook``)
==============================

.. py:function:: hook(SHELL, PID)
    :noindex:

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

.. [1] While the shorthand ``epc`` is used for commands in the ``envprobe config`` mode (see :ref:`config mode<config>`), the ``hook`` command is special, as it is meant to be available before the shell has been hooked.
     Thus, the full command name (``envprobe config ...``) must be spelled, as the shorthand is not available.


Obtaining the control commands (``consume``)
============================================

.. py:function:: consume(detach=False)

    Emit the pending changes to environment variables in the form of a shell script.
    Calling this function will *consume* the pending changes and clear the list.

    The output shell script needs to be evaluated (by calling ``eval``) in the current shell's context.

    .. warning::

        **This function is not meant to be called by the user directly!**
        Envprobe will automatically evaluate the pending changes and make them applied to the shell's state every time a new command prompt is generated.

    :param detach: If ``-d``/``--detach`` is specified, Envprobe will emit code that is meant to **unhook** it from the shell and clean up temporary files after itself.
    :type detach:  bool

    .. danger::

        Specifying ``--detach`` is a destructive operation, passing a point of no return!
        **Envprobe will irrevocably delete its temporary files related to the shell the command is executed in.**
        This will make Envprobe **in that shell** unusable.

        *Detach* is automatically performed when the shell exits, normally by the user typing in and executing ``exit`` or closing the terminal.

    :Possible invocations:
        - ``epc consume [-d]``

    :Examples:
        .. code-block:: bash

            $ ep +PATH Foo && ep FOO=Bar && epc consume
            export PATH=/Foo:...
            export FOO=Bar

    .. hint ::

        The output of this command is not directly useful for any particular purpose other than to execute the resulting script (commonly by calling ``eval`` on it) in the context of a running shell.
