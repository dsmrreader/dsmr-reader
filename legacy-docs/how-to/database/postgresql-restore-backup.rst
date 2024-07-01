Database: Restore a backup (PostgreSQL)
=======================================

Whether you can restore a backup, depends on the current state of the database.
See the pre checks below to verify some states before restore.

.. contents:: :local:
    :depth: 1


Pre checks
^^^^^^^^^^

.. hint::

    **How to check whether the database exists?**

    Execute::

        sudo -u postgres psql --list | grep dsmrreader

    If the database exists, you will see output similar to this::

         dsmrreader | dsmrreader | UTF8     | en_GB.UTF-8 | en_GB.UTF-8 |

----

.. hint::

    **How to check whether the database has a table structure?**

    Execute::

        sudo -u postgres psql -d dsmrreader -c '\dt'

    If the table structure exists, you should see a long list of tables in the output.

----

.. hint::

    **How to check whether the database has existing day/hour statistics data?**

    *This only makes sense to check if the database exists and has a table structure.*

    Execute::

        sudo -u postgres psql -d dsmrreader -c 'select count(id) as hour_count from dsmr_stats_hourstatistics';
        sudo -u postgres psql -d dsmrreader -c 'select count(id) as day_count from dsmr_stats_daystatistics';

    If the ``hour_count`` or ``day_count`` (or both) are **above zero**, then there are day and/or hour statistics stored::

         hour_count
        ------------
              45766

         day_count
        -----------
              1922

----

Importing a full backup
^^^^^^^^^^^^^^^^^^^^^^^

A full backup contains all data with its table structure and is usually named: ``dsmrreader-postgresql-backup-Friday.sql.gz``

You can only import a full backup when:

- 1. The database **does** exist.
- 2. The database **does not** contain a table structure (and thus no data).

.. hint::

    If the database does not exist, create it::

         sudo -u postgres createdb -O dsmrreader dsmrreader

.. danger::

    If it has a table structure, usually just after reinstallation, then wipe it. **This will permanently delete all data in it!**

    Execute::

        sudo supervisorctl stop all

        sudo -u postgres dropdb dsmrreader
        sudo -u postgres createdb -O dsmrreader dsmrreader

You can now import the full backup.

Execute::

    sudo supervisorctl stop all

    # For example with a backup "dsmrreader-postgresql-backup-Friday.sql.gz" in "/home/dsmr/dsmr-reader/backups/"
    sudo zcat /home/dsmr/dsmr-reader/backups/dsmrreader-postgresql-backup-Friday.sql.gz | sudo -u postgres psql dsmrreader

    sudo su - dsmr
    ./deploy.sh

    logout
    sudo supervisorctl start all

Keep an eye out for any errors during the steps above.

----

Importing a partial backup
^^^^^^^^^^^^^^^^^^^^^^^^^^

A partial backup only contains a small subset of data and is usually named: ``dsmrreader-postgresql-partial-backup-2021-03-22.sql.gz``

You can only import a partial backup when:

- 1. The database **does** exist.
- 2. The database **does** contain a table structure.
- 3. The database **does not** contain existing day/hour statistics.

.. hint::

    If the database does not exist, create it.

    Execute::

         sudo -u postgres createdb -O dsmrreader dsmrreader

.. hint::

    If the database does not have a table structure, then try creating it.
    This assumes you already reinstalled DSMR-reader.
    In the case you are still reinstalling, please finish that guide first and return after.

    Execute::

        sudo su - dsmr
        ./deploy.sh
        logout

.. danger::

    If the database already contains day/hour statistics, you probably want to abort the restore and create an issue on Github for support instead.

You can now import the partial backup.

Execute::

    # For example with a backup "dsmrreader-postgresql-partial-backup-2021-03-22.sql.gz" in "/home/dsmr/dsmr-reader/backups/"
    sudo zcat /home/dsmr/dsmr-reader/backups/dsmrreader-postgresql-partial-backup-2021-03-22.sql.gz | sudo -u postgres psql dsmrreader

Keep an eye out for any errors during the steps above.
