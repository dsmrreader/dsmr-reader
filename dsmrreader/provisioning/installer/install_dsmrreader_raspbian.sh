#!/bin/bash
set -x

# Packages
sudo apt-get install -y postgresql postgresql-server-dev-all nginx supervisor git python3 python3-pip python3-virtualenv virtualenvwrapper

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
git clone https://github.com/dennissiemensma/dsmr-reader.git /home/dsmr/dsmr-reader
chown -R dsmr:dsmr /home/dsmr/

# Virtual env
sudo sudo -u dsmr mkdir /home/dsmr/.virtualenvs
sudo sudo -u dsmr virtualenv /home/dsmr/.virtualenvs/dsmrreader --no-site-packages --python python3
echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> /home/dsmr/.bashrc
echo "cd ~/dsmr-reader" >> /home/dsmr/.bashrc

# Config & requirements
sudo sudo -u dsmr cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/django/postgresql.py /home/dsmr/dsmr-reader/dsmrreader/settings.py
sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/pip3 install -r /home/dsmr/dsmr-reader/dsmrreader/provisioning/requirements/base.txt -r /home/dsmr/dsmr-reader/dsmrreader/provisioning/requirements/postgresql.txt

# Setup
sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py migrate
sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/python3 /home/dsmr/dsmr-reader/manage.py collectstatic --noinput

# Nginx
sudo rm /etc/nginx/sites-enabled/default
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-enabled/
sudo service nginx configtest
sudo service nginx reload

# Supervisor
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr-reader.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update

echo "Installation should be completed!"