Downgrading DSMR-reader
=======================

If for some reason you need to downgrade the application, you will need to:

- unapply database migrations.
- switch the application code version to a previous release.


.. tip::

    First, **please make sure you have a recent backup of your database**!


Each release `has it's database migrations locked <https://github.com/dsmrreader/dsmr-reader/tree/v5/dsmrreader/provisioning/downgrade/>`_.
You should execute the script of the version you wish to downgrade to. And then switch the code to the release/tag accordingly.

.. tip::

    You do **not** need to downgrade to each intermediate version between your target.
    For example, if you currently run ``v5.6`` and your want to downgrade to ``v5.4``, just follow the sample below, ignoring ``v5.5`` between them.

For example when downgrading to ``v5.4``::

   sudo su - dsmr
   sh dsmrreader/provisioning/downgrade/v5.4.0.sh
   git checkout tags/v5.4.0
   ./deploy.sh

.. note::

    Unapplying the database migrations may take a while.

You should now be on the targeted release.
