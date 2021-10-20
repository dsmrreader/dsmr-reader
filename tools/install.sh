#!/usr/bin/env bash

### Please note that this script is a happy flow only and is NOT idempotent.

echo "Installing packages"
sudo apt-get install -y postgresql nginx supervisor git python3 python3-psycopg2 python3-pip python3-virtualenv

echo "Setting up database"
sudo -u postgres createuser -DSR dsmrreader
sudo -u postgres createdb -O dsmrreader dsmrreader
sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"

echo "Setting up dsmr user"
sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash
sudo usermod -a -G dialout dsmr

echo "Setting up static file folder for webserver"
sudo mkdir -p /var/www/dsmrreader/static
sudo chown -R dsmr:dsmr /var/www/dsmrreader/

echo "Cloning DSMR-reader from GitHub"
sudo git clone https://github.com/dsmrreader/dsmr-reader.git /home/dsmr/dsmr-reader
sudo chown -R dsmr:dsmr /home/dsmr/

echo "Configuring DSMR-reader"
sudo -u dsmr cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/django/settings.py.template /home/dsmr/dsmr-reader/dsmrreader/settings.py
sudo -u dsmr cp /home/dsmr/dsmr-reader/.env.template /home/dsmr/dsmr-reader/.env
sudo -u dsmr /home/dsmr/dsmr-reader/tools/generate-secret-key.sh

echo "Installing dependencies"
sudo -u dsmr pip3 install --upgrade pip poetry
sudo -u dsmr poetry config virtualenvs.in-project true
sudo -u dsmr poetry install --no-dev

echo "Applying database migrations & static files"
sudo -u dsmr /home/dsmr/dsmr-reader/.venv/bin/python3 /home/dsmr/dsmr-reader/manage.py migrate
sudo -u dsmr /home/dsmr/dsmr-reader/.venv/bin/python3 /home/dsmr/dsmr-reader/manage.py collectstatic --noinput

echo "Configuring webserver"
sudo rm /etc/nginx/sites-enabled/default
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/dsmr-webinterface /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx.service

echo "Configuring Supervisor"
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update

# Create (super)user for the DSMR-reader configuration webinterface
echo "Creating DSMR-reader superuser for webinterface"
echo "(you will be asked to choose and enter a password twice)"
sudo -u dsmr /home/dsmr/dsmr-reader/.venv/bin/python3 /home/dsmr/dsmr-reader/manage.py createsuperuser --email dsmr@localhost --username admin
