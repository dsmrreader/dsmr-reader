#!/bin/bash
# 2.11.0 to 2.10.0

./manage.py migrate dsmr_frontend 0024_v2100_release
./manage.py migrate dsmr_backend 0006_backend_auto_update_check
./manage.py migrate dsmr_weather 0004_next_sync_setting_retroactive
./manage.py migrate dsmr_mindergas 0004_mindergas_latest_sync
