#!/bin/bash
hg pull --up
./manage.py collectstatic -l
./reload.sh
