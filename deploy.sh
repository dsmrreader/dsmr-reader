#!/bin/bash
hg pull --up
pip3 install -r dsmrreader/provisioning/requirements/base.txt
./manage.py collectstatic --noinput
./manage.py migrate
./reload.sh
