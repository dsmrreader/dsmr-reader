Installation: Step by step
##########################


For others users who want some addition explanation about what they are exactly doing/installing.

Use this to host both the datalogger and application on the same machine by installing it manually.

.. tip::

    Strongly consider :doc:`using Docker containers instead <../../how-to/installation/using-docker>`, as it already contains a lot of the details (and steps) below.

    *DSMR-reader may switch to Docker-only support at some point in the future.*

.. contents:: :local:
    :depth: 2


1. Database backend (PostgreSQL)
--------------------------------

The application stores by default all readings taken from the serial cable.

- Install database::

    sudo apt-get install -y postgresql

.. tip::

    Does PostgreSQL not start/create the cluster due to locales? E.g.::

      Error: The locale requested by the environment is invalid.
      Error: could not create default cluster. Please create it manually with

      pg_createcluster 12 main start

    Try: ``dpkg-reconfigure locales``.

    Still no luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot.
    Then try ``pg_createcluster 12 main start`` again (or whatever version you are using).

Execute::

      # Check status, should be green/active
      sudo systemctl status postgresql

(!) Ignore any '*could not change directory to "/root": Permission denied*' errors for the following three commands.

- Create database user::

    sudo -u postgres createuser -DSR dsmrreader

- Create database, owned by the database user we just created::

    sudo -u postgres createdb -O dsmrreader dsmrreader

- Set password for database user::

    sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"


Optional: Restore a database backup
-----------------------------------

.. hint::

    If you need to restore a database backup with your existing data, this is the moment to do so.

    Restoring a database backup? :doc:`See here for instructions </how-to/database/postgresql-restore-backup>`.


2. Dependencies
---------------
- Now you'll have to install several utilities, required for the Nginx webserver, Gunicorn application server and cloning the application code from the GitHub repository::

    # "libopenjp2-7-dev" is due to "ImportError: libopenjp2.so.7: cannot open shared object file: No such file or directory"
    sudo apt-get install -y cu nginx supervisor git python3 python3-psycopg2 python3-pip python3-venv libopenjp2-7-dev

The CU program allows easily testing for your DSMR serial connection.
It's very basic but also very effective to simply test whether your serial cable setup works properly.


3. Application user
-------------------
The application runs as ``dsmr`` user by default. This way we do not have to run the application as ``root``, which is a bad practice anyway.

- Create user with homedir. The application will be installed in this directory and run as that user as well::

    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash

- Our user also requires dialout permissions. So allow the user to perform a dialout by adding it to the ``dialout`` group::

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

- Execute::

    logout


4. Webserver/Nginx (part 1)
---------------------------

*We will now prepare the webserver, Nginx. It will serve all application's static files directly and proxy any application requests to the backend, Gunicorn controlled by Supervisor, which we will configure later on.*

- Make sure you are **not** ``dsmr`` user here.

- Execute::

    whoami

    # Still "dsmr"? Execute CTRL+D or:
    logout

Django will later copy all static files to the directory below, used by Nginx to serve statics. Therefore it requires (write) access to it.

- Execute::

    sudo mkdir -p /var/www/dsmrreader/static

    sudo chown -R dsmr:dsmr /var/www/dsmrreader/


5. Clone project code from GitHub
---------------------------------
Now is the time to clone the code from the repository into the homedir we created.

Make sure you are currently (still) ``dsmr`` user here.

- Execute::

    whoami

    # Not "dsmr"? Execute:
    sudo su - dsmr

- Clone the repository::

    git clone --branch v5 https://github.com/dsmrreader/dsmr-reader.git

This may take a few seconds. When finished, you should see a new folder called ``dsmr-reader``, containing a clone of the GitHub repository.


6. External dependencies
------------------------

The dependencies our application uses need to be downloaded and store as well.

Make sure you are currently (still) ``dsmr`` user here.

- Execute::

    whoami

    # Not "dsmr"? Execute:
    sudo su - dsmr

- Create virtualenv::

    python3 -m venv ~/dsmr-reader/.venv/

- Ease usage of virtualenv later::

    bash -c 'echo "cd ~/dsmr-reader" >> ~/.bashrc'
    bash -c 'echo "source ~/dsmr-reader/.venv/bin/activate" >> ~/.bashrc'

You can easily test whether you've configured this correctly by logging out the ``dsmr`` user (CTRL + D or type ``logout``) and login again using ``sudo su - dsmr``.

You should see the terminal have a ``(.venv)`` prefix now, for example: ``(.venv)dsmr@rasp:~/dsmr-reader $``

Also, ``python3`` should point to the virtualenv::

    which python3

    # Expected output:
    # /home/dsmr/dsmr-reader/.venv/bin/python3

- Install dependencies (may take a minute)::

    pip3 install -r dsmrreader/provisioning/requirements/base.txt

- Setup local config::

    cp dsmrreader/provisioning/django/settings.py.template dsmrreader/settings.py

    cp .env.template .env
    ./tools/generate-secret-key.sh


7. Bootstrapping
----------------
Now it's time to bootstrap the application and check whether all settings are good and requirements are met.

Make sure you are currently (still) ``dsmr`` user here.

- Execute::

    whoami

    # Not "dsmr"? Execute:
    sudo su - dsmr

- Execute::

    ./manage.py check

It should output something similar to::

    System check identified no issues (0 silenced).

- Execute this to initialize the structure for the database we've created earlier::

    ./manage.py migrate

Prepare static files for webinterface. This will copy all static files to the directory we created for Nginx earlier in the process.
It allows us to have Nginx serve static files outside our project/code root.

- Sync static files::

    ./manage.py collectstatic --noinput

- Create an application superuser by opening the ``.env`` file with your favourite text editor. Find (or add) these lines::

    # In /home/dsmr/dsmr-reader/.env

    ### Admin credentials.
    #DSMRREADER_ADMIN_USER=
    #DSMRREADER_ADMIN_PASSWORD=

.. tip::
    Remove the ``#`` in front and add the admin username and password you'd like. E.g.::

        DSMRREADER_ADMIN_USER=admin
        DSMRREADER_ADMIN_PASSWORD=supersecretpassword

Now have DSMR-reader create/reset the admin user for you.

- Execute::

    ./manage.py dsmr_superuser


8. Webserver/Nginx (part 2)
---------------------------

You've almost completed the installation now.

.. seealso::

    This installation guide assumes you run the Nginx webserver for this application only.

    It's possible to have other applications use Nginx as well, but that requires you to remove the wildcard in the ``dsmr-webinterface`` vhost, which you will copy below.

- Make sure you are **not** ``dsmr`` user here.

- Execute::

    whoami

    # Still "dsmr"? Execute CTRL+D or:
    logout

- Remove the default Nginx vhost (**only when you do not use it yourself, see the note above**)::

    sudo rm /etc/nginx/sites-enabled/default

- Copy application vhost, **it will listen to any hostname** (wildcard), but you may change that if you feel like you need to. It won't affect the application anyway::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-available/
    sudo ln -s /etc/nginx/sites-available/dsmr-webinterface /etc/nginx/sites-enabled/

- Let Nginx verify vhost syntax and restart Nginx when the ``-t`` configtest passes::

    # Command below should output "syntax is ok" and/or "test is successful"
    sudo nginx -t

    sudo systemctl restart nginx.service


9. Supervisor
-------------
Now we configure `Supervisor <http://supervisord.org/>`_, which is used to run our application's web interface and background jobs used.
It's also configured to bring the entire application up again after a shutdown or reboot.

- Copy the configuration files for Supervisor::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/


- Enter these commands. It will ask Supervisor to recheck its config directory and use/reload the files::

    sudo supervisorctl reread
    sudo supervisorctl update

Three processes should be ``RUNNING``. Make sure they don't end up in ``ERROR`` or ``BACKOFF`` state, so refresh with the ``status`` command a few times.

- Execute::

    sudo supervisorctl status

Example of everything running well::

    dsmr_backend                     RUNNING    pid 123, uptime 0:00:06
    dsmr_datalogger                  RUNNING    pid 456, uptime 0:00:07
    dsmr_webinterface                RUNNING    pid 789, uptime 0:00:07

Want to quit supervisor? Press ``CTRL + D`` to exit supervisor command line.


.. seealso::

    :doc:`Finished? Go to setting up the application</tutorial/setting-up>`.
