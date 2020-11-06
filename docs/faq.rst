FAQ (Frequently Asked Questions)
################################


.. contents::
    :depth: 3


Application management
----------------------

How to upgrade?
^^^^^^^^^^^^^^^

Every once in a while there may be updates. You can also easily check for updates by using the application's Status page.

.. tip::

    First, **please make sure you have a recent backup of your database**!

You can update your application to the latest version by executing ``deploy.sh``, located in the root of the project.
Make sure to execute it while logged in as the ``dsmr`` user::

   sudo su - dsmr
   ./deploy.sh


How to downgrade?
^^^^^^^^^^^^^^^^^

If for some reason you need to downgrade the application, you will need to:

- unapply database migrations.
- switch the application code version to a previous release.


.. tip::

    First, **please make sure you have a recent backup of your database**!


Each release `has it's database migrations locked <https://github.com/dsmrreader/dsmr-reader/tree/v4/dsmrreader/provisioning/downgrade/>`_.
You should execute the script of the version you wish to downgrade to. And the switch the code to the release.

For example ``v4.0``::

   sudo su - dsmr
   sh dsmrreader/provisioning/downgrade/v4.0.sh
   git checkout tags/v4.0.0
   ./deploy.sh

.. note::

    Unapplying the database migrations may take a while.

You should now be on the targeted release.


How to restart?
^^^^^^^^^^^^^^^

You might want or need to restart DSMR-reader manually at some time.
E.g.: Due to altered settings that need to be reapplied to the processes.

For a soft restart::

    # This only works if the processes already run.
    sudo su - dsmr
    ./reload.sh

For a hard restart::

    # Make sure you are root or sudo user.
    sudo supervisorctl restart all


How to uninstall?
^^^^^^^^^^^^^^^^^

To remove DSMR-reader from your system, execute the following commands::

    # Nginx.
    sudo rm /etc/nginx/sites-enabled/dsmr-webinterface
    sudo service nginx reload
    sudo rm -rf /var/www/dsmrreader

    # Supervisor.
    sudo supervisorctl stop all
    sudo rm /etc/supervisor/conf.d/dsmr*.conf
    sudo supervisorctl reread
    sudo supervisorctl update

    # Homedir & user.
    sudo rm -rf /home/dsmr/
    sudo userdel dsmr

To delete your data (the database) as well::

    sudo su - postgres dropdb dsmrreader

Optionally, you can remove these packages::

    sudo apt-get remove postgresql postgresql-server-dev-all python3-psycopg2 nginx supervisor git python3-pip python3-virtualenv virtualenvwrapper


How to view logfiles?
^^^^^^^^^^^^^^^^^^^^^

.. seealso::

    :doc:`More information can be found here <troubleshooting>`.



How do I set admin credentials?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. seealso::

    :doc:`Env Settings<env_settings>`.

Configure ``DSMR_USER`` and ``DSMR_PASSWORD`` of the :doc:`Env Settings<env_settings>`.

Now execute::

    sudo su - dsmr
    ./manage.py dsmr_superuser

The user should either be created or the existing user should have its password updated.


Database
--------

How do I reclaim database disk space?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

    This will only make a difference if you've enabled data cleanup retroactively, resulting in more than a 25 percent data deletion of your entire database.

Assuming you are using the default database, PostgreSQL, you may want to try a one-time vacuum by executing::

    sudo su - postgres
    vacuumdb -f -v -d dsmrreader

If there was any disk space to reclaim, the effect should be visible on the filesystem now.


How do I change the database location?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. danger::

    Changing the database data location may cause data corruption. Only execute the step below if you understand exactly what you are doing!

Since the SD-card is quite vulnerable to wearing and corruption, you can run the database on a different disk or USB-stick.
To do this, you will have to stop the application and database, change the database configuration, move the data and restart all processes again.

Make sure the OS has direct access the new location and **create a back-up first**!

In the example below we will move the data from ``/var/lib/postgresql/`` to ``/data/postgresql/`` (which could be an external mount).

.. note::

    *Please note that "9.5" in the example below is just the version number of the database, and it may differ from your installation. The same steps however apply.*

Execute the commands below:

* Stop DSMR-reader: ``sudo supervisorctl stop all``

* Stop database: ``sudo systemctl stop postgresql``

* Confirm that the database has stopped, you should see no more ``postgresql`` processes running: ``sudo ps faux | grep postgres``

* Ensure the new location exists: ``sudo mkdir /data/postgresql/``

* Move the database data folder: ``sudo mv /var/lib/postgresql/9.5/ /data/postgresql/9.5/``

* Make sure the ``postgres`` user has access to the new location (and any parent folders in it's path): ``sudo chown -R postgres:postgres /data/``

* Edit database configuration ``sudo vi /etc/postgresql/9.5/main/postgresql.conf`` and find the line::

    data_directory = '/var/lib/postgresql/9.5/main'

* Change it to your new location::

    data_directory = '/data/postgresql/9.5/main'

* Save the file and start the database: ``sudo systemctl start postgresql``

* Check whether the database is running again, you should see multiple processes: ``sudo ps faux | grep postgres``

* Does the database not start? Check its logs in ``/var/log/postgresql/`` for hints.

* Start DSMR-reader again: ``sudo supervisorctl start all``

* Everything should work as usual now, storing the data on the new location.


How do I enable MySQL timezone support?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. seealso::

    `Check these docs <https://dev.mysql.com/doc/refman/5.7/en/mysql-tzinfo-to-sql.html>`_ for more information about how to enable timezone support on MySQL.

On recent versions it should be as simple as executing the following command as root/sudo user::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql


How do I restore a backup?
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Only follow these step if you want to restore a backup in PostgreSQL.

Restoring a backup will replace any existing data stored in the database and is irreversible!

This assumes you've **not yet** reinstalled DSMR-reader and created an **empty** database::

    sudo -u postgres createdb -O dsmrreader dsmrreader


.. warning::

    Do **not** restore your database if you've either **started the application** and/or ran ``manage.py migrate`` in some way.

    Doing so WILL cause trouble with duplicate data/ID's and break your installation at some point.


.. danger::

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



Errors
------

How do I fix ``DETAIL: Key (id)=(123) already exists``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This depends on the situation, but you can always try the following yourself first::

    # Note: dsmr_sqlsequencereset is only available in DSMR-reader v3.3.0 and higher
    sudo su - dsmr
    ./manage.py dsmr_sqlsequencereset

.. seealso::

    If it does not resolve your issue, ask for support on Github (see end of page).


How do I fix: ``Error: Already running on PID 1234``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you're seeing this error::

    Error: Already running on PID 1234 (or pid file '/var/tmp/gunicorn--dsmr_webinterface.pid' is stale)

Just delete the PID file and restart the webinterface::

    sudo supervisorctl restart dsmr_webinterface


How do I fix stats after smart meter replacement?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes, when relocating or due to replacement of your meter, the meter positions read by DSMR-reader will cause invalid data (e.g.: big gaps or inverted consumption).
Any consecutive days should not be affected by this issue, so you will only have to adjust the data for one day.

The day after, you should be able to manually adjust any invalid Day or Hour Statistics :doc:`in the admin interface<configuration>` for the invalid day.


Data
----

By default DSMR-reader reads and preserves all telegram data read.

When using a Raspberry Pi (or similar) combined with a DSMR version 5 smart meter (the default nowadays), you may experience issues after a while.

This is caused by the high data throughput of DSMR version 5, which produces a new telegram every second.
Both DSMR-reader and most of its users do not need this high frequency of telegrams to store, calculate and plot consumption data.

Therefor two measures can be taken: Increasing datalogger sleep and data retention policy.


How can I increase the datalogger sleep time?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Increase the datalogger sleep time :doc:`in the configuration<../configuration>` to 5 seconds or higher.
This will save a lot of disk storage, especially when using a Raspberry Pi SD card, usually having a size of 16 GB max.


How can I configure a data retention policy?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configure a data retention policy :doc:`in the configuration<../configuration>`.
This will eventually delete up to 99 percent of the telegrams, always preserving a few historically.
Also, day and hour totals are **never** deleted by retention policies.


.. attention::::

    New installations of DSMR-reader ``v4.1`` or higher will start with a default retention policy of one month.


I'm missing gas readings?
^^^^^^^^^^^^^^^^^^^^^^^^^

Please make sure that your meter supports reading gas consumption and that you've waited for a few hours for any graphs to render.
The gas meter positions are only be updated once per hour (for DSMR v4).
The Status page will give you insight in this as well.


How do I only use the datalogger?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. seealso::

    :doc:`More information can be found here <installation>`.


Prices
------

How do I recalculate prices retroactively?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?

Execute::

    sudo su - dsmr
    ./manage.py dsmr_stats_recalculate_prices


Support
-------

I still need help!
^^^^^^^^^^^^^^^^^^

.. tip::

    If you can't find the answer in the documentation, do not hesitate in looking for help.

    `View existing Github issues or create a new one <https://github.com/dsmrreader/dsmr-reader/issues>`_
