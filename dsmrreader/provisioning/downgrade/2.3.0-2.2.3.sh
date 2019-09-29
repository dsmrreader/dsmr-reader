#!/bin/bash
# 2.3.0 to 2.2.3

./manage.py migrate dsmr_frontend 0019_v210_release
./manage.py migrate dsmr_backup 0006_scheduled_email_backup
