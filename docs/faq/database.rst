FAQ: Database
=============

.. warning::

    Changing the database data location may cause data corruption. Only execute the step below if you understand what you are exactly doing!

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
