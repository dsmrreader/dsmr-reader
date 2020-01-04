#!/bin/bash
# 2.13.0 to 2.12.0

./manage.py migrate dsmr_frontend 0024_v2100_release
./manage.py migrate dsmr_backend 0008_scheduled_process_fields
