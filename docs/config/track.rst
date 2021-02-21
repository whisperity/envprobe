.. _config_track:

=====================================================
Changing the tracking status of variables (``track``)
=====================================================


.. py:function:: track(VARIABLE, default=False, mode=query, scope=<...>)

   Gets or sets the tracking setting for a ``VARIABLE`` (or the default
   behaviour) in the *local* or *global* ``scope``.

   The variable's tracking setting and the tracking behaviour affects whether the variable's changes are loaded from or saved to :ref:`saved snapshots<snapshots>`.

   :param VARIABLE: The name of the environment which the tracking status is accessed for, e.g. ``PATH`` or ``EDITOR``.
   :type VARIABLE: str

   :param default: If ``-d``/``--default`` is given instead of a ``VARIABLE``, the default tracing behaviour will be queried or set.
   :type default: bool

   :param mode: Either one of the following modes. If neither is specified, ``--query`` is assumed.

                * ``-t``/``--track``: set the variable to be *tracked* explicitly, or the default behaviour to track all variables that do not have an explicit setting.
                * ``-i``/``--ignore``/``--no-track``: set the variable to be *ignored* explicitly, or the default behaviour to ignore all variables that do not have an explicit setting.
                * ``-r``/``--reset``: remove the explicit setting for the variable.
                * ``-q``/``--query``: retrieve the tracking status for the variable (or the default setting), and print it to the standard output
   :type mode: choice

   :param scope: The scope of the configuration to affect.
                 There are two scopes available:

                 * ``-l``/``--local``: The setting only applies to the current shell session Envprobe is running in.
                 * ``-g``/``--global``: The setting applies to the current user's local configuration, and thus to all shells.
                   If Envprobe is not available in the current shell, only accessing the *global* configuration is possible through ``track``.

                 .. note::

                     The ``--local`` option is only available if Envprobe has been :ref:`installed and hooked<install_hook>` in the current shell.
                     If so, `scope` is *local*, unless otherwise specified.

                     If Envprobe is not available in the current shell, the ``--local`` option is not available, only ``--global`` is.
                     In this case, accessing the user-wide *global configuration* is the only option.
   :type scope: choice

   :Possible invocations:
      - ``envprobe config track VARIABLE ...``
      - ``epc track VARIABLE ...``

   :Examples:
      .. code-block:: bash

         $ epc track SOMETHING
         SOMETHING: tracked

         $ epc track --local --default --query
         local default: not configured

         $ epc track -l -d --ignore
         $ epc track SOMETHING
         SOMETHING: ignored

         $ epc track --global --track ALWAYS_TRACK
         $ epc track -l -t SOMETHING
         $ epc track SOMETHING
         SOMETHING: tracked
             local explicit TRACK

         $ epc track OTHER_THING
         OTHER_THING: ignored

         $ epc track ALWAYS_TRACK
         ALWAYS_TRACK: tracked
             global explicit TRACK

         $ epc track -l --no-track ALWAYS_TRACK
         $ epc track ALWAYS_TRACK
         ALWAYS_TRACK: ignored
             local explicit IGNORE
             global explicit TRACK

         $ epc track -l --reset SOMETHING
         $ epc track SOMETHING
         SOMETHING: ignored
