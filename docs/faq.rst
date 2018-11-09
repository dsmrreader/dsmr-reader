Frequently Asked Questions (FAQ)
================================


.. contents::
    :depth: 2


How can I update my application?
--------------------------------
The version you are running is always based on the 'latest' version of the application, called the `master` branch.
Every once in a while there may be updates. Since ``v1.5`` you can also easily check for updates by using the application's Status page.

.. warning::
    
    Before updating, **please make sure you have a recent backup of your database**! :doc:`More information about backups can be found here<application>`.

You can update your application to the latest version by executing **deploy.sh**, located in the root of the project. 
Make sure to execute it while logged in as the ``dsmr`` user::

   sudo su - dsmr
   ./deploy.sh

It will make sure to check, fetch and apply any changes released. Summary of deployment script steps:

- GIT pull (codebase update).
- PIP update requirements.
- Apply any database migrations.
- Sync static files to Nginx folder.
- Reload Gunicorn application server (web interface) and backend processes (such as the datalogger).
- Clear any caches.


How can I move the database location?
-------------------------------------
.. warning::

    Changing the database data location can cause datacorruption. Only execute the step below if you understand what you are exactly doing!

Since the SD-card is quite vulnerable to wearing and corruption, you can run the database on a different disk or USB-stick.
To do this, you will have to stop the application and database, change the database configuration, move the data and restart all processes again.

Make sure the OS has direct access the new location and **create a back-up first**!

In the example below we will move the data from ``/var/lib/postgresql/`` to ``/data/postgresql/`` (which could be an external mount).

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



Recalculate prices retroactively
--------------------------------
*I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?*

Statistics for each day are generated once, the day after. However, you can flush your statistics by executing:

``./manage.py dsmr_backend_delete_aggregated_data --statistics``

The application will delete all statistics and (slowly) regenerate them in the background. Just make sure the source data is still there.


I'm not seeing any gas readings
-------------------------------
Please make sure that your meter supports reading gas consumption and that you've waited for a few hours for any graphs to render. 
The gas meter positions are only be updated once per hour (for DSMR v4).
The Status page will give you insight in this as well.


How do I restore a database backup?
-----------------------------------

.. warning::

    Restoring a backup will replace any existing data stored in the database and is irreversible! 

.. note::

    Do you need a complete reinstall of DSMR-reader as well? 
    Then please :doc:`follow the install guide<installation>` and restore the database backup **using the notes at the end of chapter 1**. 

Only want to restore the database?

- This asumes you are still running the same application version as the backup was created in.

- Stop the application first with ``sudo supervisorctl stop all``. This will disconnect it from the database as well.

- Importing the data could take a long time. It took MySQL 15 minutes to import nearly 3 million readings, from a compressed backup, on a RaspberryPi 3. 

For **PostgreSQL** restores::

    sudo sudo -u postgres dropdb dsmrreader
    sudo sudo -u postgres createdb -O dsmrreader dsmrreader
    
    # Either restore an uncompressed (.sql) backup:
    sudo sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>
    
    # OR
    
    # Restore a compressed (.gz) backup with:
    zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo sudo -u postgres psql dsmrreader


For **MySQL** restores::

    sudo mysqladmin create dsmrreader
    sudo mysqladmin drop dsmrreader
    
    # Either restore an uncompressed (.sql) backup:
    cat <PATH-TO-MYSQL-BACKUP.sql.gz> | sudo mysql --defaults-file=/etc/mysql/debian.cnf -D dsmrreader
    
    # OR
    
    # Restore a compressed (.gz) backup with:
    zcat <PATH-TO-MYSQL-BACKUP.sql.gz> | sudo mysql --defaults-file=/etc/mysql/debian.cnf -D dsmrreader


- Start the application again with ``sudo supervisorctl start all``.

.. note::

    In case the version differs, you can try forcing a deployment reload by: ``sudo su - dsmr`` and then executing ``./post-deploy.sh``.


How do I enable timezone support for MySQL?
-------------------------------------------

`Check these docs <https://dev.mysql.com/doc/refman/5.7/en/mysql-tzinfo-to-sql.html>`_ for more information about how to enable timezone support on MySQL.
On recent versions it should be as simple as executing the following command as root/sudo user::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql



How do I retain MQTT support when upgrading to v1.23.0 or higher?
-----------------------------------------------------------------

Starting from ``v1.23.0`` DSMR-reader requires a dedicated process for processing MQTT messages (``dsmr_mqtt``).
Fresh installations automatically include the ``dsmr_mqtt`` process. Existing installations however, should add ``dsmr_mqtt`` manually. Instructions:

* Please upgrade to ``v1.23.0`` or higher first.
* Now execute the following commands as **root/sudo-user**::

    # NOTE: This will overwrite /etc/supervisor/conf.d/dsmr-reader.conf
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr-reader.conf /etc/supervisor/conf.d/
    sudo supervisorctl reread
    sudo supervisorctl update



Feature/bug report
------------------
*How can I propose a feature or report a bug I've found?*

.. seealso::
    
    `Just create a ticket at Github <https://github.com/dennissiemensma/dsmr-reader/issues/new>`_.
