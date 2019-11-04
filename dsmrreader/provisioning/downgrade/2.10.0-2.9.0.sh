#!/bin/bash
# 2.10.0 to 2.9.0

./manage.py migrate dsmr_frontend 0023_v290_release
./manage.py migrate dsmr_backend 0003_scheduled_processes
