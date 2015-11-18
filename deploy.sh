#!/bin/bash
hg pull --up
./manage.py collectstatic -l
./manage.py migrate
./reload.sh
