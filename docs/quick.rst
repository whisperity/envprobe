.. _quick:

==============
Quick overview
==============

This page contains excerpts of Envprobe's usage that detail typical everyday tasks which are helped by the tool.

.. rubric:: Table of Contents

- :ref:`Managing environment variables in the current shell<quick_envvars>`
- :ref:`Saved snapshots<quick_snapshots>`


.. rubric:: Managing environment variables in the current shell
   :name: quick_envvars

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


.. rubric:: Saved snapshots
   :name: quick_snapshots

(Read the :ref:`full documentation<snapshots>` for this section.)

    .. code-block:: bash

        $ ep %
        # (No output, initially the environment hasn't been changed yet.)

        $ ep PATH
        PATH=/usr/local/bin:/usr/bin/:/sbin:/bin

        $ ep SOME_VARIABLE=foo
        $ ep +PATH /tmp
        $ ep -PATH /sbin
        $ ep PATH+ /home/user/bin

        $ ep %
        (+) Added:       SOME_VARIABLE
                defined value: foo

        (!) Changed:     PATH
                added:         /tmp
                added:         /home/user/bin
                removed:       /sbin

        $ ep } mypath PATH
        For variable 'PATH' the element '/tmp' was added.
        For variable 'PATH' the element '/home/user/bin' was added.
        For variable 'PATH' the element '/sbin' was removed.

        $ ep } other_vars -p
        New variable 'SOME_VARIABLE' with value 'foo'.
        Save this change? (y/N) _



        $ ep list
        mypath
        other_vars

        $ ep delete mypath
        $ ep list
        other_var



        $ ep load custompaths
        For variable 'PATH' the element '/srv/custom/bin' will be added.

        $ ep PATH
        PATH=/srv/custom/bin:/tmp:/home/user/bin

        $ ep { foobar -n
        New variable 'FOO' will be created with value 'bar'.

        $ ep FOO
        FOO is not defined

        $ ep { foobar -p
        New variable 'FOO' will be created with value 'bar'.
        Load and apply this change? (y/N) _
