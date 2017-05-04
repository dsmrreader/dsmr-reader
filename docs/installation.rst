Installation
============

.. note::

    The installation guide may take about *half an hour max* (for raspberryPi 2/3), but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.


.. contents::
    :depth: 2


Dependencies & requirements
---------------------------
- **RaspberryPi 2 or 3**

.. note::

    - **Alternative #1**: You can also run it on any server near your smart meter, as long as it satisfies the other requirements.
    
    - **Alternative #2**: The application supports receiving P1 telegrams using an API, so you can also run it on a server outside your home. (:doc:`API DOCS<api>`)

.. warning::

    The RaspberryPi 1 tends to be **too slow** for this project, as it requires multi core processing.
    
    You can however run just the datalogger client on an old RaspberryPi, :doc:`see for the API for a howto and example scripts<api>`.

- **Raspbian OS**

 - Recommended and tested with, but any OS satisfying the requirements should do fine.

- **Python 3.4+**

.. warning::

    Support for ``Python 3.3`` has been **discontinued** since ``DSMR-reader v1.5`` (due to Django).

- **PostgreSQL 9+ database**

.. warning::

    Support for ``MySQL`` has been **deprecated** since ``DSMR-reader v1.6`` and will be discontinued completely in a later release.
    Please use a PostgreSQL database instead. Users already running MySQL will be supported in migrating at a later moment.

- **Smart Meter** with support for **at least DSMR 4.x+** and a **P1 telegram port**

 - Tested so far with Landis+Gyr E350, Kaifa.

- **Minimal 1 GB of disk space on RaspberryPi (card)** (for application installation & virtualenv). 

 - More disk space is required for storing all reader data captured (optional). I generally advise to use a 8+ GB SD card. 
 - The readings will take about 90+ percent of the disk space. Retention is on it's way for a future release in 2017. 

- **Smart meter P1 data cable** 

 - Can be purchased online and they cost around 15 tot 20 Euro's each.
 
- **Basic Linux knowledge for deployment, debugging and troubleshooting**

 - It just really helps if you know what you are doing.


1. Database backend (PostgreSQL)
--------------------------------

The application stores by default all readings taken from the serial cable.
There is support for **PostgreSQL**, and there used to be support for **MySQL/MariaDB** as well.
The latter is currently deprecated by this project and support will be discontinued in a future release. 

Install PostgreSQL, ``postgresql-server-dev-all`` is required for the virtualenv installation later in this guide.

- Install database::

    sudo apt-get install -y postgresql postgresql-server-dev-all

Does Postgres not start due to locales? Try: ``dpkg-reconfigure locales``. 
Still no luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot.

(!) Ignore any '*could not change directory to "/root": Permission denied*' errors for the following three commands.

- Create database user::

    sudo sudo -u postgres createuser -DSR dsmrreader

- Create database, owned by the database user we just created::

    sudo sudo -u postgres createdb -O dsmrreader dsmrreader

- Set password for database user::

    sudo sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"

.. note::

    **Optional**: Do you need to restore a **PostgreSQL** database backup as well?
    
    Restore an uncompressed (``.sql``) backup with::
    
        sudo sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>

    Or restore a compressed (``.gz``) backup with::
    
        zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo sudo -u postgres psql dsmrreader

Now continue at chapter 2 below (Dependencies).

(Legacy) MySQL/MariaDB
^^^^^^^^^^^^^^^^^^^^^^^^^
.. warning::

    Support for the MySQL database backend is deprecated and will be removed in a later release.
    Please use a PostgreSQL database instead. Users already running MySQL will be supported in migrating at a later moment.
    
Install MariaDB. You can also choose to install the closed source MySQL, as they should be interchangeable anyway. 
``libmysqlclient-dev`` is required for the virtualenv installation later in this guide.

- Install database::

    sudo apt-get install -y mariadb-server-10.0 libmysqlclient-dev

- Create database::

    sudo mysqladmin --defaults-file=/etc/mysql/debian.cnf create dsmrreader

- Create database user::

    echo "CREATE USER 'dsmrreader'@'localhost' IDENTIFIED BY 'dsmrreader';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v

- Set privileges for database user::

    echo "GRANT ALL ON dsmrreader.* TO 'dsmrreader'@'localhost';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v

- Flush privileges to activate them::

    sudo mysqladmin --defaults-file=/etc/mysql/debian.cnf reload

.. note::

    **Optional**: Do you need to restore a **MySQL** database backup as well?
    
    Restore an uncompressed (``.sql``) backup with::
    
        cat <PATH-TO-MYSQL-BACKUP.sql.gz> | sudo mysql --defaults-file=/etc/mysql/debian.cnf -D dsmrreader

    Or restore a compressed (``.gz``) backup with::
    
        zcat <PATH-TO-MYSQL-BACKUP.sql.gz> | sudo mysql --defaults-file=/etc/mysql/debian.cnf -D dsmrreader


2. Dependencies
---------------
Now you'll have to install several utilities, required for the Nginx webserver, Gunicorn application server and cloning the application code from the Github repository::

    sudo apt-get install -y nginx supervisor git python3 python3-pip python3-virtualenv virtualenvwrapper

Install ``cu``. The CU program allows easy testing for your DSMR serial connection. 
It's very basic but also very effective to simply test whether your serial cable setup works properly::

    sudo apt-get install -y cu

    
3. Application user
-------------------
The application runs as ``dsmr`` user by default. This way we do not have to run the application as ``root``, which is a bad practice anyway.

Create user with homedir. The application code and virtualenv will reside in this directory as well::

    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash

Our user also requires dialout permissions. So allow the user to perform a dialout by adding it to the ``dialout`` group::

    sudo usermod -a -G dialout dsmr

Either proceed to the next heading **for a test reading** or continue at chapter 4.


Your first reading (optional)
-----------------------------

.. note::

    **OPTIONAL**: You may skip this section as it's not required for the application to install. However, if you have never read your meter's P1 telegram port before, I recommend to perform an initial reading to make sure everything works as expected.

- Now login as the user we have just created, to perform our very first reading! ::

    sudo su - dsmr

- Test with ``cu`` for **DSMR 4+**::

    cu -l /dev/ttyUSB0 -s 115200 --parity=none -E q

- Or test with ``cu`` for **DSMR 2.2** (untested)::

    cu -l /dev/ttyUSB0 -s 9600 --parity=none

You now should see something similar to ``Connected.`` and a wall of text and numbers *within 10 seconds*. Nothing? Try different BAUD rate, as mentioned above. You might also check out a useful blog, `such as this one (Dutch) <http://gejanssen.com/howto/Slimme-meter-uitlezen/>`_.

- To exit cu, type "``q.``", hit Enter and wait for a few seconds. It should exit with the message ``Disconnected.``.


4. Webserver/Nginx (part 1)
---------------------------

*We will now prepare the webserver, Nginx. It will serve all application's static files directly and proxy any application requests to the backend, Gunicorn controlled by Supervisor, which we will configure later on.*

- Make sure you are acting here as ``root`` or ``sudo`` user. If not, press CTRL + D to log out of the ``dsmr`` user.

Django will later copy all static files to the directory below, used by Nginx to serve statics. Therefor it requires (write) access to it::

    sudo mkdir -p /var/www/dsmrreader/static
    
    sudo chown -R dsmr:dsmr /var/www/dsmrreader/


5. Clone project code from Github
---------------------------------
Now is the time to clone the code from the repository into the homedir we created. 

- Make sure you are now acting as ``dsmr`` user (if not then enter: ``sudo su - dsmr``)

- Clone the repository::

    git clone https://github.com/dennissiemensma/dsmr-reader.git

This may take a few seconds. When finished, you should see a new folder called ``dsmr-reader``, containing a clone of the Github repository.    


6. Virtualenv
-------------

The dependencies our application uses are stored in a separate environment, also called **VirtualEnv**. 

Although it's just a folder inside our user's homedir, it's very effective as it allows us to keep dependencies isolated or to run different versions of the same package on the same machine. 
`More information about this subject can be found here <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

- Make sure you are still acting as ``dsmr`` user (if not then enter: ``sudo su - dsmr``)

- Create folder for the virtualenv(s) of this user::

    mkdir ~/.virtualenvs

- Create a new virtualenv, we usually use the same name for it as the application or project::

    virtualenv ~/.virtualenvs/dsmrreader --no-site-packages --python python3

.. note::

    Note that it's important to specify **Python 3** as the default interpreter.

- Put both commands below in the ``dsmr`` user's ``~/.bashrc`` file with your favorite text editor::

    source ~/.virtualenvs/dsmrreader/bin/activate
    
    cd ~/dsmr-reader

This will both **activate** the virtual environment and cd you into the right directory on your **next login** as ``dsmr`` user.

.. note::
    
    You can easily test whether you've configured this correctly by logging out the ``dsmr`` user (CTRL + D) and login again using ``sudo su - dsmr``.

    You should see the terminal have a ``(dsmrreader)`` prefix now, for example: ``(dsmrreader)dsmr@rasp:~/dsmr-reader $``

Make sure you've read and executed the note above, because you'll need it for the next chapter. 


7. Application configuration & setup
------------------------------------
The application will also need the appropriate database client, which is not installed by default. 
For this I created two ready-to-use requirements files, which will also install all other dependencies required, such as the Django framework. 

The ``base.txt`` contains requirements which the application needs anyway, no matter which backend you've choosen.

.. note::

    **Installation of the requirements below might take a while**, depending on your Internet connection, RaspberryPi speed and resources (generally CPU) available. Nothing to worry about. :]

PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^
- Did you choose PostgreSQL? Then execute these two lines::

    cp dsmrreader/provisioning/django/postgresql.py dsmrreader/settings.py

    pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/postgresql.txt


Did everything install without fatal errors? If the database client refuses to install due to missing files/configs, 
make sure you've installed ``postgresql-server-dev-all`` earlier in the process, when you installed the database server itself.

Continue to chapter 8 (Bootstrapping).

(Legacy) MySQL/MariaDB
^^^^^^^^^^^^^^^^^^^^^^^^^
.. warning::

    Support for the MySQL database backend is deprecated and will be removed in a later release.
    Please use a PostgreSQL database instead. Users already running MySQL will be supported in migrating at a later moment.

- Or did you choose MySQL/MariaDB? Execute these two commands::

    cp dsmrreader/provisioning/django/mysql.py dsmrreader/settings.py

    pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/mysql.txt

Did everything install without fatal errors? If the database client refuses to install due to missing files/configs, 
make sure you've installed ``libmysqlclient-dev`` earlier in the process, when you installed the database server itself.


8. Bootstrapping
----------------
Now it's time to bootstrap the application and check whether all settings are good and requirements are met.
 
- Execute this to initialize the database we've created earlier::

    ./manage.py migrate

Prepare static files for webinterface. This will copy all static files to the directory we created for Nginx earlier in the process. 
It allows us to have Nginx serve static files outside our project/code root.

- Sync static files::

    ./manage.py collectstatic --noinput

Create an application superuser. Django will prompt you for a password. The credentials generated can be used to access the administration panel inside the application.  
Alter username and email if you prefer other credentials, but email is not used in the application anyway.

- Create your user::

    ./manage.py createsuperuser --username admin --email root@localhost

.. note::

    Because you have shell access you may reset your user's password at any time (in case you forget it). Just enter this for a password reset::

    ./manage.py changepassword admin

You've almost completed the installation now.

    
9. Webserver/Nginx (part 2)
---------------------------

.. note::

    This installation guide asumes you run the Nginx webserver for this application only.
    
    It's possible to have other applications use Nginx as well, but that requires you to remove the wildcard in the ``dsmr-webinterface`` vhost, which you will copy below.

- Make sure you are acting here as ``root`` or ``sudo`` user. If not, press CTRL + D to log out of the ``dsmr`` user.

Remove the default Nginx vhost (**only when you do not use it yourself, see the note above**)::

        sudo rm /etc/nginx/sites-enabled/default

- Copy application vhost, **it will listen to any hostname** (wildcard), but you may change that if you feel like you need to. It won't affect the application anyway::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-enabled/

- Let Nginx verify vhost syntax and reload Nginx when ``configtest`` passes::

    sudo service nginx configtest

    sudo service nginx reload



10. Supervisor
--------------
Now we configure `Supervisor <http://supervisord.org/>`_, which is used to run our application's web interface and background jobs used. 
It's also configured to bring the entire application up again after a shutdown or reboot.

- Copy the configuration file for Supervisor::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr-reader.conf /etc/supervisor/conf.d/

- Login to ``supervisorctl`` management console::

    sudo supervisorctl

- Enter these commands (**listed after the** ``>``). It will ask Supervisor to recheck its config directory and use/reload the files::

    supervisor> reread

    supervisor> update
    
Three processes should be started or running. Make sure they don't end up in ``ERROR`` or ``BACKOFF`` state, so refresh with the ``status`` command a few times.

- When still in ``supervisorctl``'s console, type::

    supervisor> status

Example of everything running well::

    dsmr_backend                     RUNNING    pid 123, uptime 0:00:06
    dsmr_datalogger                  RUNNING    pid 456, uptime 0:00:07
    dsmr_webinterface                RUNNING    pid 789, uptime 0:00:07

- Want to check whether the datalogger works? Just tail it's log in supervisor with::

    supervisor> tail -f dsmr_datalogger
    
You should see similar output as the ``cu``-command printed earlier in the installation process.

Want to quit supervisor? ``CTRL + C`` to stop tailing and then ``CTRL + D`` once to exit supervisor command line.


You now should have everything up and running! We're almost done and just need to do a few last things on the next page.
