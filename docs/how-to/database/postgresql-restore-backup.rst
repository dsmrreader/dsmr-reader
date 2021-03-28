Database: Restore a backup (PostgreSQL)
=======================================

First check whether situation A or B applies to you below.

Situation A: Already finished DSMR-reader reinstallation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. danger::

    The steps below replace any existing data stored in the database and is irreversible!

    You cannot merge a database backup with an existing installation containing data you want to preserve!

    Doing so **will** cause trouble with duplicate data/ID's and **break** your installation at some point.

If you just finished reinstalling DSMR-reader but **did not** restore the backup and you want to **overwrite** the data in it::

    sudo supervisorctl stop all

    sudo -u postgres dropdb dsmrreader
    sudo -u postgres createdb -O dsmrreader dsmrreader

    # For example with a backup "dsmrreader-postgresql-backup-Sunday.sql.gz" in "/home/dsmr/dsmr-reader/backups/"
    # Execute:
    sudo zcat /home/dsmr/dsmr-reader/backups/dsmrreader-postgresql-backup-Sunday.sql.gz | sudo -u postgres psql dsmrreader

    sudo su - dsmr
    ./deploy.sh

    logout
    sudo supervisorctl start all


Situation B: Currently reinstalling DSMR-reader
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are still in the process of reinstalling DSMR-reader and just executed these commands::

    ...

    sudo -u postgres createuser -DSR dsmrreader
    sudo -u postgres createdb -O dsmrreader dsmrreader
    sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"

Your database **should** still be empty and this will import any backup made::

    # For example with a backup "dsmrreader-postgresql-backup-Sunday.sql.gz" in "/home/dsmr/dsmr-reader/backups/"
    # Execute:
    sudo zcat /home/dsmr/dsmr-reader/backups/dsmrreader-postgresql-backup-Sunday.sql.gz | sudo -u postgres psql dsmrreader

Now continue the installation guide.

.. attention::

    You should **not** see any errors regarding duplicate data or existing ID's or whatever.

    If you do encounter errors while restoring the backup in an **empty** database, create an issue at GitHub and **do not continue**.
