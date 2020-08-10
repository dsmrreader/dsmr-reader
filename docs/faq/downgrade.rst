FAQ: Downgrading the application
================================

If for some reason you need to downgrade the application, you will need to:

- unapply database migrations.
- switch the application code version to a previous release.


.. warning::
    
    First, **please make sure you have a recent backup of your database**! :doc:`More information about backups can be found here<../data_integrity>`.


Each release `has it's database migrations locked<https://github.com/dennissiemensma/dsmr-reader/tree/v4/dsmrreader/provisioning/downgrade>`.
You should execute the script of the version you wish to downgrade to. And the switch the code to the release.

For example ``v4.0``::

   sudo su - dsmr
   sh dsmrreader/provisioning/downgrade/v4.0.sh
   git checkout tags/v4.0.0
   ./deploy.sh

.. note::

    Unapplying the database migrations may take a while.

You should now be on the targeted release.
