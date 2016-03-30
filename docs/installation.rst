Installation
============

The installation guide may take about *half an hour max* (for raspberryPi 2/3), but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.

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


Dependencies
------------
Several utilities, required for webserver, application server and cloning the application code from the repository::

    sudo apt-get install -y nginx supervisor git python3 python3-pip python3-virtualenv virtualenvwrapper

Install ``cu``. The CU program allows easy testing for your DSMR serial connection. It's basic but very effective to test whether your serial cable setup works properly. ::

    sudo apt-get install -y cu

    
Application user
----------------
The application runs as ``dsmr`` user by default. This way we do not have to run the application as ``root``, which is a bad practice anyway.

Create user with homedir. The application code and virtualenv resides in this directory as well::

    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash

Our user also requires ``dialout`` permissions. So allow the user to perform a dialout by adding it to the group::

    sudo usermod -a -G dialout dsmr


Webserver (Nginx), part 1
-------------------------
We will now prepare the webserver, Nginx. It will serve all application's static files directly and proxy application requests to the backend, Gunicorn controlled by Supervisor, which we will configure later on.

Django will copy all static files to a separate directory, used by Nginx to serve statics::

    sudo mkdir -p /var/www/dsmrreader/static
    
    sudo chown -R dsmr:dsmr /var/www/dsmrreader/

*The reason for splitting the webserver chapter in two steps, is because the application requires the directory created above to exist. And Nginx requires the application to exist (cloned) before running (and to copy its virtual hosts file), resulting in an dependency loop... :]*


Your first reading (optional)
-----------------------------
You may skip this section as it's not required for the application to install. However, if you have never read your meter before, I recommend to perform an initial reading to make sure everything works as expected.

- Now login as the user we just created, to perform our very first reading! ::

    sudo su - dsmr

- Test with ``cu`` (BAUD rate settings for **DSMR v4** is ``115200``, for older verions it should be ``9600``)::

    cu -l /dev/ttyUSB0 -s 115200 --parity=none -E q

You now should see something similar to ``Connected.`` and a wall of text and numbers within 10 seconds. Nothing? Try different BAUD rate, as mentioned above. You might also check out a useful blog, `such as this one (Dutch) <http://gejanssen.com/howto/Slimme-meter-uitlezen/>`_.

- To exit cu, type "``q.``", hit Enter and wait for a few seconds. It should exit with the message ``Disconnected.``.


Clone project code from Github
------------------------------
Now is the time to clone the code from the repository and check it out on your device. 

- Make sure you are still acting as ``dsmr`` user (if not then enter: ``sudo su - dsmr``)

- Clone the repository::

    git clone https://github.com/dennissiemensma/dsmr-reader.git

This may take a few seconds. When finished, you should see a new folder called ``dsmr-reader``, containing a clone of the Github repository.    


Virtualenv
----------
The dependencies our application uses are stored in a separate environment, also called **VirtualEnv**. Although it's just a folder inside our user's homedir, it's very effective as it allows us to keep dependencies isolated or to run different versions of the same package on the same machine. `More information about this subject can be found here <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

- Make sure you are still acting as ``dsmr`` user (if not then enter: ``sudo su - dsmr``)

- Create folder for the virtualenvs of this user::

    mkdir ~/.virtualenvs

- Create a new virtualenv, we usually use the same name for it as the application or project. Note that it's important to specify python3 as the default interpreter::

    virtualenv ~/.virtualenvs/dsmrreader --no-site-packages --python python3

Now *activate* the environment. It effectively directs all aliases for software installed in the virtualenv to the binaries inside the virtualenv.

I.e. the Python binary inside ``/usr/bin/python`` won't be used when the virtualenv is activated, but ``/home/dsmr/.virtualenvs/dsmrreader/bin/python`` will be instead.

- Activate virtualenv & cd to project::

    source ~/.virtualenvs/dsmrreader/bin/activate
    
    cd ~/dsmr-reader

You might want to put the ``source ~/.virtualenvs/dsmrreader/bin/activate`` command above in the user's ``~/.bashrc`` (logout and login to test). I also advice to put the ``cd ~/dsmr-reader`` in there as well, which will cd you directly inside the project folder on login.


Application configuration & setup
---------------------------------
Earlier in this guide you had to choose for either **(A.) PostgreSQL** or **(B.) MySQL/MariaDB**. Our application needs to know which backend used in order to communicate with it. 

Therefor I created two default (Django-)settings files you can copy, one for each backend. The application will also need the appropiate database client, which is not installed by default. For this I also created two ready-to-use requirements files, which will also install all other dependencies required, such as the Django framework. 

The ``base.txt`` contains requirements which the application needs anyway, no matter which backend you've choosen.

- (!) Note: *Installation might take a while*, depending on your Internet connection, RaspberryPi version and resources (generally CPU) available. Nothing to worry about. :]

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

