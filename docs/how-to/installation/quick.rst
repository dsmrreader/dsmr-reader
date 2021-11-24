Installation: Quick
###################

Use this to host both the datalogger and application on the same machine by installing it manually.

Contains just a list of commands needed for the installation of DSMR-reader.

.. tip::

    Strongly consider :doc:`using Docker containers instead <../../how-to/installation/using-docker>`, as it already contains a lot of the details (and steps) below.

    *DSMR-reader may switch to Docker-only support at some point in the future.*

.. contents:: :local:
    :depth: 1


System packages
---------------

Execute::

    # Packages
    sudo apt-get install -y postgresql cu nginx supervisor git python3 python3-psycopg2 python3-pip

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

Continue::

    # Database
    sudo -u postgres createuser -DSR dsmrreader
    sudo -u postgres createdb -O dsmrreader dsmrreader
    sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"


Optional: Restore a database backup
-----------------------------------

.. hint::

    If you need to restore a database backup with your existing data, this is the moment to do so.

    Restoring a database backup? :doc:`See here for instructions </how-to/database/postgresql-restore-backup>`.


DSMR-reader
-----------

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

    # Dependencies
    sudo pip3 install poetry
    sudo -u dsmr poetry config virtualenvs.in-project true
    sudo sh -c 'echo "cd ~/dsmr-reader" >> /home/dsmr/.bashrc'
    sudo sh -c 'echo "poetry shell" >> /home/dsmr/.bashrc'
    sudo su - dsmr
    poetry install --no-dev
    CTRL + D (exit)
    CTRL + D (logout)

    # Config
    sudo -u dsmr cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/django/settings.py.template /home/dsmr/dsmr-reader/dsmrreader/settings.py
    sudo -u dsmr cp /home/dsmr/dsmr-reader/.env.template /home/dsmr/dsmr-reader/.env
    sudo -u dsmr /home/dsmr/dsmr-reader/tools/generate-secret-key.sh

    # Requirements
    sudo -u dsmr /home/dsmr/dsmr-reader/.venv/bin/pip3 install -r /home/dsmr/dsmr-reader/dsmrreader/provisioning/requirements/base.txt

    # Setup
    sudo -u dsmr /home/dsmr/dsmr-reader/.venv/bin/python3 /home/dsmr/dsmr-reader/manage.py migrate
    sudo -u dsmr /home/dsmr/dsmr-reader/.venv/bin/python3 /home/dsmr/dsmr-reader/manage.py collectstatic --noinput

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
    sudo supervisorctl status

.. seealso::

    :doc:`See here for setting up admin credentials<../admin/set-username-password>`.

.. seealso::

    :doc:`Finished? Go to setting up the application</tutorial/setting-up>`.
