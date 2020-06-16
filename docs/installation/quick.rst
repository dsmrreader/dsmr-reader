Installation: Quick
===================

.. note::

    The installation guide may take about *15 to 30 minutes* (for raspberryPi 2/3), but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.


Start::

    # Packages
    sudo apt-get install -y postgresql nginx supervisor git python3 python3-psycopg2 python3-pip python3-virtualenv virtualenvwrapper
    
.. note::
    
    Does PostgreSQL not start/create the cluster due to locales? E.g.::
    
      Error: The locale requested by the environment is invalid.
      Error: could not create default cluster. Please create it manually with
    
      pg_createcluster 9.4 main --start
 
    
    Try: ``dpkg-reconfigure locales``. 
    
    Still no luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot.
    Then try ``pg_createcluster 9.4 main --start`` again (or whatever version you are using).

Continue::
    
    # Database
    sudo sudo -u postgres createuser -DSR dsmrreader
    sudo sudo -u postgres createdb -O dsmrreader dsmrreader
    sudo sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"
    
    # System user
    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash
    sudo usermod -a -G dialout dsmr
    
    # Nginx
    sudo mkdir -p /var/www/dsmrreader/static
    sudo chown -R dsmr:dsmr /var/www/dsmrreader/
    
    # Code checkout
    sudo git clone https://github.com/dennissiemensma/dsmr-reader.git /home/dsmr/dsmr-reader
    sudo chown -R dsmr:dsmr /home/dsmr/
    
    # Virtual env
    sudo sudo -u dsmr mkdir /home/dsmr/.virtualenvs
    sudo sudo -u dsmr virtualenv /home/dsmr/.virtualenvs/dsmrreader --system-site-packages --python python3
    sudo sh -c 'echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> /home/dsmr/.bashrc'
    sudo sh -c 'echo "cd ~/dsmr-reader" >> /home/dsmr/.bashrc'
    
    # Config & requirements
    sudo sudo -u dsmr cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/django/postgresql.py /home/dsmr/dsmr-reader/dsmrreader/settings.py
    sudo sudo -u dsmr /home/dsmr/dsmr-reader/tools/generate-secret-key.sh
    sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/pip3 install -r /home/dsmr/dsmr-reader/dsmrreader/provisioning/requirements/base.txt

    sudo su - dsmr

    # Setup
    sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py migrate
    sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py collectstatic --noinput

    # Nginx
    sudo rm /etc/nginx/sites-enabled/default
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-available/
    sudo ln -s /etc/nginx/sites-available/dsmr-webinterface /etc/nginx/sites-enabled/
    sudo service nginx configtest
    sudo service nginx reload
    
    # Supervisor
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_client.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/
    sudo supervisorctl reread
    sudo supervisorctl update
    
    # Create application user
    sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py createsuperuser --username admin --email root@localhost


----


:doc:`Finished? Go to setting up the application<../application>`.

