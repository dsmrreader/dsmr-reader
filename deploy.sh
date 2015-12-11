#!/bin/bash
hg pull --up
./manage.py collectstatic --noinput
./manage.py migrate
./reload.sh
