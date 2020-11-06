Installation
############

.. tip::

    Choose either option A, B, C or D below.

.. contents::
    :depth: 2


Option A: Install DSMR-reader manually (quick)
==============================================

.. note::

    Use this to host both the datalogger and application on the same machine by installing it manually.

    Contains just a list of commands needed for the installation of DSMR-reader.


.. contents:: :local:
    :depth: 1


Part 1
------

Execute::

    # Packages
    sudo apt-get install -y postgresql nginx supervisor git python3 python3-psycopg2 python3-pip python3-virtualenv virtualenvwrapper

.. attention::

    Does PostgreSQL not start/create the cluster due to locales? E.g.::

      Error: The locale requested by the environment is invalid.
      Error: could not create default cluster. Please create it manually with

      pg_createcluster 9.4 main --start


    Try: ``dpkg-reconfigure locales``.

    Still no luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot.
    Then try ``pg_createcluster 9.4 main --start`` again (or whatever version you are using).

Continue::

    # Database
    sudo -u postgres createuser -DSR dsmrreader
    sudo -u postgres createdb -O dsmrreader dsmrreader
    sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"

Optional: Restore a database backup
-----------------------------------

.. tip::

    If you need to restore a database backup with your existing data, this is the moment to do so.

    Restoring a database backup? :doc:`See the FAQ for instructions <faq>`.


Part 2
------

Continue::

    # System user
    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash
    sudo usermod -a -G dialout dsmr

    # Nginx
    sudo mkdir -p /var/www/dsmrreader/static
    sudo chown -R dsmr:dsmr /var/www/dsmrreader/

    # Code checkout
    sudo git clone https://github.com/dsmrreader/dsmr-reader.git /home/dsmr/dsmr-reader
    sudo chown -R dsmr:dsmr /home/dsmr/

    # Virtual env
    sudo -u dsmr mkdir /home/dsmr/.virtualenvs
    sudo -u dsmr virtualenv /home/dsmr/.virtualenvs/dsmrreader --system-site-packages --python python3
    sudo sh -c 'echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> /home/dsmr/.bashrc'
    sudo sh -c 'echo "cd ~/dsmr-reader" >> /home/dsmr/.bashrc'

    # Config
    sudo -u dsmr cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/django/settings.py.template /home/dsmr/dsmr-reader/dsmrreader/settings.py
    sudo -u dsmr cp /home/dsmr/dsmr-reader/.env.template /home/dsmr/dsmr-reader/.env
    sudo -u dsmr /home/dsmr/dsmr-reader/tools/generate-secret-key.sh

    # Open /home/dsmr/dsmr-reader/.env and enter the superuser credentials
    # you wish to use, when running 'manage.py dsmr_superuser' later.
    DSMR_USER=???
    DSMR_PASSWORD=???

    # Requirements
    sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/pip3 install -r /home/dsmr/dsmr-reader/dsmrreader/provisioning/requirements/base.txt

    # Setup
    sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py migrate
    sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py collectstatic --noinput

    # Nginx
    sudo rm /etc/nginx/sites-enabled/default
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-available/
    sudo ln -s /etc/nginx/sites-available/dsmr-webinterface /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx.service

    # Supervisor
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/
    sudo supervisorctl reread
    sudo supervisorctl update

    # Create (super)user with the values in DSMR_USER and
    # DSMR_PASSWORD as defined in one of the previous steps.
    sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py dsmr_superuser


.. seealso::

    :doc:`Finished? Go to setting up the application<../application>`.


----


Option B: Install DSMR-reader manually (explained)
==================================================

.. note::

    For others users who want some addition explanation about what they are exactly doing/installing.

    Use this to host both the datalogger and application on the same machine by installing it manually.


.. contents:: :local:
    :depth: 2


1. Database backend (PostgreSQL)
--------------------------------

The application stores by default all readings taken from the serial cable.

- Install database::

    sudo apt-get install -y postgresql

.. note::

    Does PostgreSQL not start/create the cluster due to locales? E.g.::

      Error: The locale requested by the environment is invalid.
      Error: could not create default cluster. Please create it manually with

      pg_createcluster 9.4 main --start

    Try: ``dpkg-reconfigure locales``.

    Still no luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot.
    Then try ``pg_createcluster 9.4 main --start`` again (or whatever version you are using).

(!) Ignore any '*could not change directory to "/root": Permission denied*' errors for the following three commands.

- Create database user::

    sudo -u postgres createuser -DSR dsmrreader

- Create database, owned by the database user we just created::

    sudo -u postgres createdb -O dsmrreader dsmrreader

- Set password for database user::

    sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"


Optional: Restore a database backup
-----------------------------------

.. tip::

    If you need to restore a database backup with your existing data, this is the moment to do so.

    Restoring a database backup? :doc:`See the FAQ for instructions <faq>`.


2. Dependencies
---------------
Now you'll have to install several utilities, required for the Nginx webserver, Gunicorn application server and cloning the application code from the Github repository::

    sudo apt-get install -y nginx supervisor git python3 python3-psycopg2 python3-pip python3-virtualenv virtualenvwrapper

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


Optional: Your first reading
----------------------------

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

    git clone https://github.com/dsmrreader/dsmr-reader.git

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

    virtualenv ~/.virtualenvs/dsmrreader --system-site-packages --python python3

.. note::

    Note that it's important to specify **Python 3** as the default interpreter.

- Each time you work as ``dsmr`` user, you will have to switch to the virtualenv with these commands::

    source ~/.virtualenvs/dsmrreader/bin/activate
    cd ~/dsmr-reader

- Let's have both commands executed **automatically** every time we login as ``dsmr`` user, by adding them ``~/.bashrc`` file::

    sh -c 'echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> ~/.bashrc'
    sh -c 'echo "cd ~/dsmr-reader" >> ~/.bashrc'

This will both activate the virtual environment and cd you into the right directory on your **next login** as ``dsmr`` user.

.. note::

    You can easily test whether you've configured this correctly by logging out the ``dsmr`` user (CTRL + D) and login again using ``sudo su - dsmr``.

    You should see the terminal have a ``(dsmrreader)`` prefix now, for example: ``(dsmrreader)dsmr@rasp:~/dsmr-reader $``

Make sure you've read and executed the note above, because you'll need it for the next chapter.


7. Application configuration & setup
------------------------------------
The application will also need the appropriate database client, which is not installed by default.
For this I created two ready-to-use requirements files, which will also install all other dependencies required, such as the Django framework.


Setup local config::

    cp dsmrreader/provisioning/django/settings.py.template dsmrreader/settings.py

    cp .env.template .env
    ./tools/generate-secret-key.sh

.. note::

    **Installation of the requirements below might take a while**, depending on your Internet connection, RaspberryPi speed and resources (generally CPU) available. Nothing to worry about. :]

Install dependencies::

    pip3 install -r dsmrreader/provisioning/requirements/base.txt


8. Bootstrapping
----------------
Now it's time to bootstrap the application and check whether all settings are good and requirements are met.

- Execute this to initialize the database we've created earlier::

    ./manage.py migrate

Prepare static files for webinterface. This will copy all static files to the directory we created for Nginx earlier in the process.
It allows us to have Nginx serve static files outside our project/code root.

- Sync static files::

    ./manage.py collectstatic --noinput

Create an application superuser with the following command.
The ``DSMR_USER`` and ``DSMR_PASSWORD`` :doc:`as defined in Env Settings<../env_settings>` will be used for the credentials.

Execute::

    ./manage.py dsmr_superuser

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

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-available/
    sudo ln -s /etc/nginx/sites-available/dsmr-webinterface /etc/nginx/sites-enabled/

- Let Nginx verify vhost syntax and restart Nginx when the ``-t`` configtest passes::

    sudo nginx -t

    sudo systemctl restart nginx.service


10. Supervisor
--------------
Now we configure `Supervisor <http://supervisord.org/>`_, which is used to run our application's web interface and background jobs used.
It's also configured to bring the entire application up again after a shutdown or reboot.

- Copy the configuration files for Supervisor::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/

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

Want to quit supervisor? Press ``CTRL + D`` to exit supervisor command line.


.. seealso::

    :doc:`Finished? Go to setting up the application<../application>`.


----


Option C: Install DSMR-reader using Docker
==========================================

+------------+------------------------------------------------------+
| Author     | ``xirixiz`` (Bram van Dartel)                        |
+------------+------------------------------------------------------+
| Github     | https://github.com/xirixiz/dsmr-reader-docker        |
+------------+------------------------------------------------------+
| Docker Hub | https://hub.docker.com/r/xirixiz/dsmr-reader-docker/ |
+------------+------------------------------------------------------+


.. seealso::

    :doc:`Finished? Go to setting up the application<../application>`.


----


Option D: Install datalogger only
=================================

.. note::

    This will install a datalogger that will forward telegrams to a remote instance of DSMR-reader, using its API.

.. contents:: :local:
    :depth: 1

The remote datalogger script has been overhauled in DSMR-reader ``v4.1``.
If you installed a former version, reconsider reinstalling it completely with the new version below.

.. attention::

    To be clear, there should be two hosts:

    - The device hosting the remote datalogger
    - The device (or server) hosting the receiving DSMR-reader instance

Receiving DSMR-reader instance
------------------------------

Make sure to first prepare the API at the DSMR-reader instance you'll forward the telegrams to.
You can enable the API and view/edit the API key used :doc:`in the configuration<../configuration>`.

.. tip::

    If your smart meter only supports DSMR v2 (or you are using a non Dutch smart meter), make sure to change the DSMR version :doc:`in the configuration<../configuration>` as well, to have DSMR-reader parse them correctly.

Also, you should disable the datalogger process over there, since you won't be using it anyway::

    sudo rm /etc/supervisor/conf.d/dsmr_datalogger.conf
    sudo supervisorctl reread
    sudo supervisorctl update

Remote datalogger device
------------------------

Switch to the device you want to install the remote datalogger on.

Execute::

    # Packages
    sudo apt-get install -y supervisor python3 python3-pip python3-virtualenv virtualenvwrapper

    # System user
    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash
    sudo usermod -a -G dialout dsmr
    sudo chown -R dsmr:dsmr /home/dsmr/

    # Virtual env
    sudo -u dsmr mkdir /home/dsmr/.virtualenvs
    sudo -u dsmr virtualenv /home/dsmr/.virtualenvs/dsmrreader --system-site-packages --python python3
    sudo sh -c 'echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> /home/dsmr/.bashrc'

    # Requirements
    sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/pip3 install pyserial==3.4 requests==2.24.0 python-decouple==3.3


Datalogger script
^^^^^^^^^^^^^^^^^

Create a new file ``/home/dsmr/dsmr_datalogger_api_client.py`` with the following contents: `dsmr_datalogger_api_client.py on GitHub <https://github.com/dsmrreader/dsmr-reader/blob/v4/dsmr_datalogger/scripts/dsmr_datalogger_api_client.py>`_

Or execute the following to download it directly to the path above::

    sudo wget -O /home/dsmr/dsmr_datalogger_api_client.py https://raw.githubusercontent.com/dsmrreader/dsmr-reader/v4/dsmr_datalogger/scripts/dsmr_datalogger_api_client.py


API config (``.env``)
^^^^^^^^^^^^^^^^^^^^^

.. hint::

    The ``.env`` file below is not mandatory to use. Alternatively you can specify all settings mentioned below as system environment variables.

Create another file ``/home/dsmr/.env`` and add as contents::

    ### The DSMR-reader API('s) to forward telegrams to:
    DATALOGGER_API_HOSTS=
    DATALOGGER_API_KEYS=

Keep the file open for multiple edits / additions below.

Add the schema (``http://``/``https://``) and hostname/port to ``DATALOGGER_API_HOSTS``. Add the API key to ``DATALOGGER_API_KEYS``. For example::

    # Example with default port:
    DATALOGGER_API_HOSTS=http://12.34.56.78
    DATALOGGER_API_KEYS=1234567890ABCDEFGH

    # Example with non standard port, e.g. Docker:
    DATALOGGER_API_HOSTS=http://12.34.56.78:7777
    DATALOGGER_API_KEYS=0987654321HGFEDCBA

.. tip::

    Are you using the remote datalogger for multiple instances of DSMR-reader? Then use ``DATALOGGER_API_HOSTS`` and ``DATALOGGER_API_KEYS`` as comma separated lists::

        # Example with multiple DSMR-reader installations:
        DATALOGGER_API_HOSTS=http://12.34.56.78,http://87.65.43.21:7777
        DATALOGGER_API_KEYS=1234567890ABCDEFGH,0987654321HGFEDCBA

        ### API host "http://12.34.56.78"      uses API key "1234567890ABCDEFGH"
        ### API host "http://87.65.43.21:7777" uses API key "0987654321HGFEDCBA"


Serial port or network socket config?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Choose either ``A.`` or ``B.`` below.


A. Serial port (``.env``)
^^^^^^^^^^^^^^^^^^^^^^^^^
Are you using a cable to read telegrams directly from a serial port?

Then add the following contents to ``/home/dsmr/.env``::

    DATALOGGER_INPUT_METHOD=serial
    DATALOGGER_SERIAL_PORT=/dev/ttyUSB0
    DATALOGGER_SERIAL_BAUDRATE=115200

When using a different port or baud rate, change the ``DATALOGGER_SERIAL_PORT`` / ``DATALOGGER_SERIAL_BAUDRATE`` values accordingly.


B. Network socket (``.env``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Are you using a network socket for reading the telegrams? E.g.: ``ser2net``.

Then add the following contents to ``/home/dsmr/.env``::

    DATALOGGER_INPUT_METHOD=ipv4
    DATALOGGER_NETWORK_HOST=
    DATALOGGER_NETWORK_PORT=

Set the hostname or IP address in ``DATALOGGER_NETWORK_HOST`` and the port in ``DATALOGGER_NETWORK_PORT``.


Other settings (``.env``)
^^^^^^^^^^^^^^^^^^^^^^^^^

These settings are **optional** but can be tweaked when required:

- ``DATALOGGER_TIMEOUT``: The timeout in seconds that applies to reading the serial port and/or writing to the DSMR-reader API. Omit to use the default value.

- ``DATALOGGER_SLEEP``: The time in seconds that the datalogger will pause after each telegram written to the DSMR-reader API. Omit to use the default value.

- ``DATALOGGER_DEBUG_LOGGING``: Set to ``true`` or ``1`` to enable verbose debug logging. Omit to disable. Warning: Enabling this logging for a long period of time on a Raspberry Pi may cause accelerated wearing of your SD card!

Supervisor
^^^^^^^^^^

.. hint::

    The following steps are also meant for the device you've just installed the remote datalogger on.

Create a new supervisor config in ``/etc/supervisor/conf.d/dsmr_remote_datalogger.conf`` with contents::

    [program:dsmr_remote_datalogger]
    command=/home/dsmr/.virtualenvs/dsmrreader/bin/python3 -u /home/dsmr/dsmr_datalogger_api_client.py
    pidfile=/var/tmp/dsmrreader--%(program_name)s.pid
    user=dsmr
    group=dsmr
    autostart=true
    autorestart=true
    startsecs=1
    startretries=100
    stopwaitsecs=20
    redirect_stderr=true
    stdout_logfile=/var/log/supervisor/%(program_name)s.log
    stdout_logfile_maxbytes=10MB
    stdout_logfile_backups=3


Have Supervisor reread and update its configs to initialize the process::

    sudo supervisorctl reread
    sudo supervisorctl update


The script should now forward telegrams to the API host(s) you specified.

