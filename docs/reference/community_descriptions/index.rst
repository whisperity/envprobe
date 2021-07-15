.. _impl_descriptions:

======================
Community descriptions
======================

.. currentmodule:: envprobe.community_descriptions

Envprobe implements the programs responsible for interfacing with the :ref:`Variable Descriptions Knowledge Base<community_descriptions>` in the :py:mod:`community_descriptions` module.

Local storage
=============

.. currentmodule:: envprobe.community_descriptions.local_data

The data downloaded from the knowledge-base is stored in a dedicated location (see :py:func:`envprobe.settings.get_data_directory`), separate from the user's own configuration.
The :py:class:`MetaConfiguration` class allows accessing the metadata of the storage.

.. autofunction:: get_storage_configuration
.. autoclass:: MetaConfiguration
   :members:

The individual configuration for variables can be accessed through a :py:class:`envprobe.settings.variable_information.VariableInformation` instance, in the exact same fashion as the user's local configuration is accessible.

.. autofunction:: get_variable_information_manager

Downloader
==========

.. currentmodule:: envprobe.community_descriptions.downloader

The following program elements are used from the higher-level logic to handle downloading and unpacking the contents of the knowledge-base.

.. autofunction:: fetch_latest_version_information
.. autofunction:: download_latest_data

.. autoclass:: DescriptionSource
    :members:
    :special-members: __len__, __iter__, __getitem__

Layout of the knowledge-base repository
=======================================

The repository is hosted on `GitHub <http://github.com/whisperity/Envprobe-Descriptions>`_ and managed as a separate Git repository.

``format.ver``
--------------

The format of the repository is versioned internally and the current version of the data files in the commit is specified in the ``format.ver`` file.
Versions are expressed in the `X.Y` (major and minor version) format.
Envprobe will only accept the download if the format is supported.

.. currentmodule:: envprobe.community_descriptions.downloader

.. autodata:: MIN_SUPPORTED_FORMAT
.. autodata:: MAX_SUPPORTED_FORMAT

Data files (``something.csv``)
------------------------------

The data itself is stored in *comma-separated values* (CSV) files.
(Read more about CSV files in the :py:mod:`csv` module documentation.)
CSV files allow easy editing and diffing of the files, and also easy handling during download.

The CSV file beings with a header row that defines the title of each column.
Each data file identifies a conceptual "group" of variables by usage, scope, or associated context.
However, the downloader merges the information from **all** data files together when creating the local copy.

.. code-block:: csv

    Variable,TypeKind,Description
    __META__,COMMENT,"Example datafile."
    MY_VARIABLE,string,"A variable."
    NAMES,comma_separated,"A list of names."

.. currentmodule:: envprobe.community_descriptions.schema_doc

.. autoclass:: Record
    :members:
    :member-order: bysource

.. autoclass:: MetaRecord
    :members:
    :member-order: bysource
