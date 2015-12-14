#!/bin/bash
hg pull --up
pip3 install -r requirements/base.txt
./manage.py collectstatic --noinput
./manage.py migrate
./reload.sh
