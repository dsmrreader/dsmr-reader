Installation: Restore database backup
=====================================

.. note::

    Only follow these step if you want to restore a backup in PostgreSQL.

Restoring a backup will replace any existing data stored in the database and is irreversible!

This assumes you've **not yet** reinstalled DSMR-reader and created an **empty** database::

    sudo -u postgres createdb -O dsmrreader dsmrreader


.. attention::

    Do **not** restore your database if you've either **started the application** and/or ran ``manage.py migrate`` in some way.

    Doing so WILL cause trouble with duplicate data/ID's and break your installation at some point.


.. warning::

    To be clear, we'll repeat it once again:

    Do **not** restore your database if you've either **started the application** and/or ran ``manage.py migrate`` in some way.

    Doing so WILL cause trouble with duplicate data/ID's and break your installation at some point.


Compressed (default)
^^^^^^^^^^^^^^^^^^^^
To restore a compressed backup (``.gz``), run::

    zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo -u postgres psql dsmrreader


Uncompressed (legacy)
^^^^^^^^^^^^^^^^^^^^^
To restore an uncompressed backup (``.sql``), run::

    sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>


Result
^^^^^^

You should **not** see any errors regarding duplicate data or existing ID's or whatever.

.. attention::

    If you do encounter errors while restoring the backup in an **empty** database, create an issue at Github and **do not continue**.

