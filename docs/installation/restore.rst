Installation: Restore database backup
=====================================

.. warning::

    Only follow these step if you want to restore a backup in PostgreSQL.

.. warning::

    Restoring a backup will replace any existing data stored in the database and is irreversible!

This assumes you've already reinstalled DSMR-reader and created an **empty** database.

Compressed (default)
^^^^^^^^^^^^^^^^^^^^
To restore a compressed backup (``.gz``), run::

    zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo sudo -u postgres psql dsmrreader

Uncompressed (legacy)
^^^^^^^^^^^^^^^^^^^^^
To restore an uncompressed backup (``.sql``), run::

    sudo sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>
