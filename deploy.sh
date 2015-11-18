#!/bin/bash
hg pull --up
./manage.py collectstatic --noinput --link
./manage.py migrate
./reload.sh
