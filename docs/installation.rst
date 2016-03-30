Installation
############

The installation guide may take about half an hour max, but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.

Database backend
----------------
The application stores by default all readings taken from the serial cable. Depending on your needs, you can choose for either (Option A.) PostgreSQL (Option B.) MySQL/MariaDB. If you have no idea what to choose, I generally advise to pick PostgreSQL, as it has better support for timezone handling (needed for DST transitions).

(Option A.) PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^
Install PostgreSQL, postgresql-server-dev-all is required for the virtualenv installation later in this guide.

- Install database::

    sudo apt-get install -y postgresql postgresql-server-dev-all

Postgres does not start due to locales? Try: dpkg-reconfigure locales

No luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot

(!) Ignore any '*could not change directory to "/root": Permission denied*' errors for the following three commands.

- Create user::

    sudo sudo -u postgres createuser -DSR dsmrreader

- Create database, owned by the user we just created::

    sudo sudo -u postgres createdb -O dsmrreader dsmrreader

- Set password for user::

    sudo sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"


(Option B.) MySQL/MariaDB
^^^^^^^^^^^^^^^^^^^^^^^^^
Install MariaDB. You can also choose to install the closed source MySQL, as they should be interchangeable anyway. libmysqlclient-dev is required for the virtualenv installation later in this guide.

- Install database::

    sudo apt-get install -y mariadb-server-10.0 libmysqlclient-dev

- Create database::

    sudo mysqladmin create dsmrreader

- Create user::

    echo "CREATE USER 'dsmrreader'@'localhost' IDENTIFIED BY 'dsmrreader';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v

- Set privileges for user::

    echo "GRANT ALL ON dsmrreader.* TO 'dsmrreader'@'localhost';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v

- Flush privileges to activate them::

    mysqladmin reload

 