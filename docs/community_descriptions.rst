.. _community_descriptions:

====================================
Variable Descriptions Knowledge Base
====================================

The **Envprobe Variable Descriptions Knowledge Base** is a sister project to *Envprobe* which aims to aggregate the :ref:`settings<config_set>`, such as the variable's :ref:`type<vartype_safety>`, about environment variables that are commonly used across the world.

The canonical repository where the knowledge-base lives is available on `GitHub at whisperity/Envprobe-Descriptions <http://github.com/whisperity/Envprobe-Descriptions>`_.

Using this additional information, Envprobe can automatically configure its own behaviour towards a variable from an additional source of information.
If the user's local settings do not contain any setting, and the built-in heuristics do not say anything about a variable, this source will be used.

.. note::
    The knowledge-base is **NOT** installed automatically when Envprobe is :ref:`downloaded<install>` to your machine.
    The ``envprobe config descriptions update`` :ref:`command<config_descriptions_update>` must be executed manually to fetch the initial data, and subsequent updates.

Installing or updating
======================

Execute the ``envprobe config descriptions update`` command as shown below.
The process is automatic and self-contained, and will update the local copy of the knowledge-base.

.. code-block:: bash

    $ envprobe config descriptions update
    Checking for latest version of the Envprobe Variable Descriptions Knowledge Base project.
    Extracting 'default'...
            extracted 7 variables.
    Extracting 'python'...
            extracted 10 variables.
    Cleaning up old information...
            cleaned up 2 records.

    $ envprobe config descriptions update
    Checking for latest version of the Envprobe Variable Descriptions Knowledge Base project.
    Nothing to update - the latest data is already available.

Contribute to the project
=========================

If you would like to contribute to the knowledge-base project, please submit an `issue <http://github.com/whisperity/envprobe-descriptions/issues/new>`_ or a pull request.
:ref:`Advanced details about the project's layout<impl_descriptions>` is available in the *Implementation reference* section.
