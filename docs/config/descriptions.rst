.. _config_descriptions:

=====================================================================
Interface with the community descriptions database (``descriptions``)
=====================================================================

The ``descriptions`` commands allows interfacing the :ref:`community descriptions<community_descriptions>` knowledge-base with its local copy.
This command is implemented with further subcommands, which you need to choose from.

.. _config_descriptions_update:

Update the *community descriptions* database (``update``)
=========================================================

.. py:function:: descriptions update()
    :noindex:

    Check if the description project's repository has a newer version available.
    If so, download, extract and install the data contained therein.
    Subsequent calls to Envprobe will behave according to the new information.

    :Possible invocations:
        - ``envprobe config descriptions update``
        - ``epc descriptions update``

    .. important::
        This command **requires** Internet access, and will connect to `GitHub <http://github.com/whisperity/Envprobe-Descriptions>`_ to download the new information.

    .. note::
        The :ref:`local settings of the user<config_set>` for a variable will take priority, and are stored in a location separate from where the community descriptions are stored.
