Installation
============
The installation guide may take about *half an hour max* (for raspberryPi 2/3), but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.


Dependencies & requirements
---------------------------
- **RaspberryPi 2 or 3**

 - RaspberryPi 1 should work decently, but I do not actively support it.

- **Raspbian OS**

 - Recommended and tested with, but any OS satisfying the requirements should do fine.

- **Python 3.3 / 3.4 / 3.5**
- **PostgreSQL 9+ or MySQL / MariaDB 5.5+**

 - I highly recommend *PostgreSQL* due to builtin support for timezones.

- **Smart Meter** with support for **at least DSMR 4.0/4.2** and **P1 telegram port**

 - Tested so far with Landis+Gyr E350, Kaifa. Telegram port looks like an RJ11 (phone) socket.

- **Minimal 100 MB of disk space on RaspberryPi (card)** (for application installation & virtualenv). 

 - More disk space is required for storing all reader data captured (optional). I generally advise to use a 8+ GB SD card. 
 - The readings will take 90+ percent of the disk space. I plan however to add some kind of retention to it later, keeping the data (of many years) far below the 500 MB. 

- **Smart meter P1 data cable** 

  - Can be purchased online and they cost around 15 tot 20 Euro's each.

- **Basic Linux knowledge for deployment, debugging and troubleshooting**

 - It just really helps if you know what you are doing.


1. Database backend
-------------------

The application stores by default all readings taken from the serial cable. Depending on your needs, you can choose for either (Option A.) **PostgreSQL** (Option B.) **MySQL/MariaDB**. 

*If you have no idea what to choose, I generally advise to pick PostgreSQL, as it has builtin support for (local) timezone handling (required for DST transitions).*

(Option A.) PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^
Install PostgreSQL, ``postgresql-server-dev-all`` is required for the virtualenv installation later in this guide.

- Install database::

    sudo apt-get install -y postgresql postgresql-server-dev-all

Does Postgres not start due to locales? Try: ``dpkg-reconfigure locales``.  Still no luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot.

(!) Ignore any '*could not change directory to "/root": Permission denied*' errors for the following three commands.

- Create database user::

    sudo sudo -u postgres createuser -DSR dsmrreader

- Create database, owned by the database user we just created::

    sudo sudo -u postgres createdb -O dsmrreader dsmrreader

- Set password for database user::

    sudo sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"


(Option B.) MySQL/MariaDB
^^^^^^^^^^^^^^^^^^^^^^^^^
Install MariaDB. You can also choose to install the closed source MySQL, as they should be interchangeable anyway. ``libmysqlclient-dev`` is required for the virtualenv installation later in this guide.

- Install database::

    sudo apt-get install -y mariadb-server-10.0 libmysqlclient-dev

- Create database::

    sudo mysqladmin create dsmrreader

- Create database user::

    echo "CREATE USER 'dsmrreader'@'localhost' IDENTIFIED BY 'dsmrreader';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v

- Set privileges for database user::

    echo "GRANT ALL ON dsmrreader.* TO 'dsmrreader'@'localhost';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v

- Flush privileges to activate them::

    mysqladmin reload


2. Dependencies
---------------
Now you'll have to install several utilities, required for the Nginx webserver, Gunicorn application server and cloning the application code from the Github repository::

    sudo apt-get install -y nginx supervisor git python3 python3-pip python3-virtualenv virtualenvwrapper

Install ``cu``. The CU program allows easy testing for your DSMR serial connection. It's very basic but also very effective to simply test whether your serial cable setup works properly. ::

    sudo apt-get install -y cu

    
3. Application user
-------------------
The application runs as ``dsmr`` user by default. This way we do not have to run the application as ``root``, which is a bad practice anyway.

Create user with homedir. The application code and virtualenv will reside in this directory as well::

    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash

Our user also requires dialout permissions. So allow the user to perform a dialout by adding it to the ``dialout`` group::

    sudo usermod -a -G dialout dsmr


4. Webserver/Nginx (part 1)
---------------------------

*We will now prepare the webserver, Nginx. It will serve all application's static files directly and proxy any application requests to the backend, Gunicorn controlled by Supervisor, which we will configure later on.*

Django will copy all static files to a separate directory, used by Nginx to serve statics. Therefor it requires (write) access to it::

    sudo mkdir -p /var/www/dsmrreader/static
    
    sudo chown -R dsmr:dsmr /var/www/dsmrreader/

*The reason for splitting the webserver chapter in two steps, is because the application requires the directory created above to exist. And Nginx requires the application to exist (cloned) before running (and to copy its virtual hosts file), resulting in an dependency loop.*

Either proceed to the next heading for a test reading or continue at step 5.


Your first reading (optional)
-----------------------------
**OPTIONAL**: You may skip this section as it's not required for the application to install. However, if you have never read your meter's P1 telegram port before, I recommend to perform an initial reading to make sure everything works as expected.

- Now login as the user we have just created, to perform our very first reading! ::

    sudo su - dsmr

- Test with ``cu`` for **DSMR 4+**::

    cu -l /dev/ttyUSB0 -s 115200 --parity=none -E q

- Or test with ``cu`` for **DSMR 2.2** (untested)::

    cu -l /dev/ttyUSB0 -s 9600 --parity=none

You now should see something similar to ``Connected.`` and a wall of text and numbers *within 10 seconds*. Nothing? Try different BAUD rate, as mentioned above. You might also check out a useful blog, `such as this one (Dutch) <http://gejanssen.com/howto/Slimme-meter-uitlezen/>`_.

- To exit cu, type "``q.``", hit Enter and wait for a few seconds. It should exit with the message ``Disconnected.``.


5. Clone project code from Github
---------------------------------
Now is the time to clone the code from the repository into the homedir we created. 

- Make sure you are still acting as ``dsmr`` user (if not then enter: ``sudo su - dsmr``)

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

- Create a new virtualenv, we usually use the same name for it as the application or project. Note that it's important to specify **python3** as the default interpreter::

    virtualenv ~/.virtualenvs/dsmrreader --no-site-packages --python python3

Now *activate* the environment. It effectively directs all aliases for software installed in the virtualenv to the binaries inside the virtualenv.
I.e. the Python binary inside ``/usr/bin/python`` won't be used when the virtualenv is activated, but ``/home/dsmr/.virtualenvs/dsmrreader/bin/python`` will be instead.

- Activate virtualenv & cd to project::

    source ~/.virtualenvs/dsmrreader/bin/activate
    
    cd ~/dsmr-reader

You might want to put the ``source ~/.virtualenvs/dsmrreader/bin/activate`` command above in the user's ``~/.bashrc`` (logout and login to test).

I also advice to put the ``cd ~/dsmr-reader`` in there as well, which will cd you directly inside the project folder on login.


7. Application configuration & setup
------------------------------------
Earlier in this guide you had to choose for either **(A.) PostgreSQL** or **(B.) MySQL/MariaDB**. Our application needs to know which backend used in order to communicate with it. 

Therefor I created two default (Django-)settings files you can copy, one for each backend. The application will also need the appropriate database client, which is not installed by default. For this I also created two ready-to-use requirements files, which will also install all other dependencies required, such as the Django framework. 

The ``base.txt`` contains requirements which the application needs anyway, no matter which backend you've choosen.

- (!) Note: **Installation of the requirements below might take a while**, depending on your Internet connection, RaspberryPi speed and resources (generally CPU) available. Nothing to worry about. :]

(Option A.) PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^
- Did you choose PostgreSQL? Then execute these two lines::

    cp dsmrreader/provisioning/django/postgresql.py dsmrreader/settings.py

    pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/postgresql.txt

(Option B.) MySQL/MariaDB
^^^^^^^^^^^^^^^^^^^^^^^^^
- Or did you choose MySQL/MariaDB? Execute these two commands::

    cp dsmrreader/provisioning/django/mysql.py dsmrreader/settings.py

    pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/mysql.txt


Did everything install without fatal errors? If either of the database clients refuses to install due to missing files/configs, 
make sure you've installed ``postgresql-server-dev-all`` (for **PostgreSQL**) or ``libmysqlclient-dev`` (for **MySQL**) earlier in the process, 
when you installed the database server itself.


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
Alter username and email if you prefer other credentials, but email is not (yet) used in the application anyway. 

Since you have shell access you may reset your user's password at any time (in case you forget it). Just enter this for a password reset: ``./manage.py changepassword admin``

- Create user inside application::

    ./manage.py createsuperuser --username admin --email root@localhost

    
9. Webserver/Nginx (part 2)
---------------------------
Go back to ``root``/``sudo-user`` to config webserver (press ``CTRL + D`` once).

- **OPTIONAL**: Remove the default Nginx vhost (*only when you do not use it yourself*)::

    sudo rm /etc/nginx/sites-enabled/default

- Copy application vhost, *it will listen to any hostname* (wildcard), but you may change that if you feel like you need to. It won't affect the application anyway::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-enabled/

- Let Nginx verify vhost syntax and reload Nginx when ``configtest`` passes::

    sudo service nginx configtest

    sudo service nginx reload



10. Supervisor
--------------
Now we configure `Supervisor <http://supervisord.org/>`_, which is used to run our application's web interface and background jobs used. 
It's also configured to bring the entire application up again after a shutdown or reboot.

- Each job has it's own configuration file, so make sure to copy them all::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_*.conf /etc/supervisor/conf.d/

- Login to ``supervisorctl`` management console::

    sudo supervisorctl

- Enter these commands (listed after the ``>``). It will ask Supervisor to recheck its config directory and use/reload the files::

    supervisor> reread

    supervisor> update
    
Three processes should be started or running. Make sure they don't end up in ``ERROR`` or ``BACKOFF`` state, so refresh with '``status``' a few times.

- When still in ``supervisorctl``'s console, type::

    supervisor> status

Example of everything running well::

    dsmr_backend                     STARTING
    dsmr_datalogger                  RUNNING
    dsmr_webinterface                RUNNING

- Want to check whether the datalogger works? Just tail it's log in supervisor with::

    supervisor> tail -f dsmr_datalogger
    
Please note that due to Supervisor's output buffering **it might take a minute or two before you see any output**. You should see similar output as the ``cu``-command printed earlier in the installation process.

Want to quit supervisor? ``CTRL + C`` to stop tail and ``CTRL + D`` once to exit supervisor command line.


You now should have everything up and running! We're almost done, but only need to check a just few more things in the next chapters.
