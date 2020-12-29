.. _quick:

==============
Quick overview
==============

This page contains excerpts of Envprobe's usage that detail typical everyday tasks which are helped by the tool.

.. rubric:: Table of Contents

- :ref:`Managing environment variables in the current shell<quick_managing>`


.. rubric:: Managing environment variables in the current shell
   :name: quick_managing

(Read the :ref:`full documentation<envvars>` for this section.)

.. code-block:: bash

   $ ep get USER
   USER=root

   $ ep USER
   USER=root

   $ ep PATH
   PATH=/usr/local/bin:/usr/bin:/sbin:/bin

   $ echo $SOME_VARIABLE
   # No result, variable is not defined.
   $ ep SOME_VARIABLE=MyValue
   $ echo $SOME_VARIABLE
   MyValue

   $ ep ^SOME_VARIABLE
   $ echo $SOME_VARIABLE
   # No result.


   $ fancy
   fancy: command not found!

   $ ep +PATH /opt/fancy/bin
   $ fancy
   Fancy tool works!

   $ ep PATH
   PATH=/opt/fancy/bin:/usr/local/bin:/usr/bin:/sbin:/bin

   $ pwd
   /root

   $ ep -PATH /opt/fancy/bin
   $ ep PATH+ .
   $ ep PATH
   PATH=/usr/local/bin:/usr/bin:/sbin:/bin:/root

   $ ep +PATH ..
   PATH=/:/usr/local/bin:/usr/bin:/sbin:/bin:/root
