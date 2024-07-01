Uninstalling DSMR-reader
========================

To remove DSMR-reader from your system, execute the following commands::

    # Nginx.
    sudo rm /etc/nginx/sites-enabled/dsmr-webinterface
    sudo service nginx reload
    sudo rm -rf /var/www/dsmrreader

    # Supervisor.
    sudo supervisorctl stop all
    sudo rm /etc/supervisor/conf.d/dsmr*.conf
    sudo supervisorctl reread
    sudo supervisorctl update

    # Homedir & user.
    sudo rm -rf /home/dsmr/
    sudo userdel dsmr

To delete your data (the database) as well::

    sudo -u postgres dropdb dsmrreader

Optionally, you can remove these packages::

    sudo apt-get remove postgresql postgresql-server-dev-all python3-psycopg2 nginx supervisor git python3-pip python3-virtualenv virtualenvwrapper
