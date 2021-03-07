.. _install:

=======
Install
=======

Envprobe requires at least Python **3.6** to be installed on the system.
Apart from Python and one of the supported POSIX-compatible shells, there are no additional dependencies.

Obtaining Envprobe
==================

You can download Envprobe from the `official repository <http://github.com/whisperity/Envprobe>`_, either using `Git <http://git-scm.org>`_ or a ``tar`` download.
Extract the downloaded files to any location comfortable.
In the documentation, we will use ``~/envprobe`` as the location where Envprobe is installed to.

.. code-block:: bash
   :caption: Downloading via *Git*

   git clone http://github.com/whisperity/envprobe.git ~/envprobe \
       --origin upstream --single-branch --branch master --depth 1


.. code-block:: bash
   :caption: Downloading the current version from GitHub as a release

   mkdir ~/envprobe
   wget http://github.com/whisperity/envprobe/tarball/master -O envprobe.tar.gz
   tar xzf envprobe.tar.gz --strip-components=1 -C ~/envprobe/

.. _install_hook:

Setting up the shell hook
=========================

Envprobe can work its "magic" and apply the changes to the running shell's environment through a *hook* which is executed every time a prompt is generated.
This hook must be registered for the executed shell before using Envprobe.
The easiest way to have the hook registered is by adding the invocation of Envprobe's hook generator to the configuration file of the shell you are using.

.. Warning::

    Envprobe's hook execution at the start of the shell involves considering the environment as-is at that moment to be the initial state used by the :ref:`saved snapshots<snapshots>` feature.
    Because scripts loaded after Envprobe can change the state of environment and result in otherwise unintended, automated changes picked up by Envprobe as if the user made them, it is **well-advised to load Envprobe last**.


Bash
----

Put the following code as-is (including quotes, etc.) at the end of ``~/.bashrc``:

.. code-block:: bash

    eval "$(~/envprobe/envprobe config hook bash $$)";

Zsh
---

Stock Zsh
~~~~~~~~~

Put the following code as-is (including quotes, etc.) at the end of ``~/.zshrc``:

.. code-block:: bash

    eval "$(~/envprobe/envprobe config hook zsh $$)";


Zsh with *Oh-My-Zsh*
~~~~~~~~~~~~~~~~~~~~

If you are using `Oh-My-Zsh <http://ohmyz.sh>`_ to manage your Zsh, create a new file ``~/.oh-my-zsh/custom/zzzzzz_envprobe.zsh`` with the following contents as-is (including quotes, etc.):

.. code-block:: bash

    eval "$(~/envprobe/envprobe config hook zsh $$)";


Testing the hook
================

If Envprobe is successfully installed, the hook code itself will register the shell *functions* ``envprobe``, and ``envprobe-config``, and their shorthand aliases ``ep``, and ``epc``, for the :ref:`main mode<main>` and :ref:`config mode<config>`, respectively.

After adding the hook script to your configuration, start a new shell, and type in ``ep``.
If something similar to the following is visible on the screen (instead of a *"bash: Command not found"* or a *"python: No module named"* error), Envprobe is working as intended:

.. code-block:: bash

    $ ep
    usage: envprobe [-h] ...



Officially supported configuration
==================================

Below are the configuration combinations that the `continuous integration testing <http://github.com/whisperity/Envprobe/actions>`_ is done for.
However, due to Envprobe being a straightforward tool, other distributions are expected to work fine.

.. role:: raw-html(raw)
   :format: html

+--------------------------------------+-----------------------------------+--------------------------------------------------------------+
| Operating system                     |         Required dependencies     | Shells supported                                             |
+--------------------------------------+-----------------------------------+--------------------------------------------------------------+
| Ubuntu 18.04 LTS (*Bionic Beaver*)   |    Python :raw-html:`&ge;` 3.6    | Bash (:raw-html:`&ge;` 4.4), Zsh (:raw-html:`&ge;` 5.4)      |
+--------------------------------------+-----------------------------------+--------------------------------------------------------------+
| Ubuntu 20.04 LTS (*Focal Fossa*)     |    Python :raw-html:`&ge;` 3.8    | Bash (:raw-html:`&ge;` 5.0), Zsh (:raw-html:`&ge;` 5.8)      |
+--------------------------------------+-----------------------------------+--------------------------------------------------------------+

