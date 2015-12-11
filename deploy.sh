#!/bin/bash
hg pull --up
./manage.py collectstatic --noinput
./manage.py migrate
./reload.sh
pip3 install -r requirements/base.txt
