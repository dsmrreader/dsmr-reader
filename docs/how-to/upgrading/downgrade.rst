Downgrading DSMR-reader
=======================

If for some reason you need to downgrade the application, you will need to:

- unapply database migrations.
- switch the application code version to a previous release.


.. tip::

    First, **please make sure you have a recent backup of your database**!


Each release `has it's database migrations locked <https://github.com/dsmrreader/dsmr-reader/tree/v5/dsmrreader/provisioning/downgrade/>`_.
You should execute the script of the version you wish to downgrade to. And the switch the code to the release.

For example when downgrading to ``v5.4``::

   sudo su - dsmr
   sh dsmrreader/provisioning/downgrade/v5.4.sh
   git checkout tags/v5.4.0
   ./deploy.sh

.. note::

    Unapplying the database migrations may take a while.

You should now be on the targeted release.
