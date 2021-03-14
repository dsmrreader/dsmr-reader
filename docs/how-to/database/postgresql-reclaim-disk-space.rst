Database: Reclaiming disk space (PostgreSQL)
============================================

.. note::

    This will only make a difference if you've enabled data cleanup retroactively, resulting in roughly more than a 25 percent data deletion of your entire database.

Assuming you are using the default database, PostgreSQL, you may want to try a one-time vacuum by executing::

    sudo su - postgres
    vacuumdb -f -v -z -d dsmrreader

If there was any disk space to reclaim, the effect should be visible on the filesystem now.
