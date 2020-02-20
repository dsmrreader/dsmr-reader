#!/bin/bash

# Dump for DSMR-reader v3.5
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0014_verbose_field_translations
./manage.py migrate dsmr_backup 0008_verbose_field_translations
./manage.py migrate dsmr_consumption 0015_track_power_current
./manage.py migrate dsmr_datalogger 0020_track_power_current
./manage.py migrate dsmr_frontend 0033_django_colorfield_update
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0013_process_sleep
./manage.py migrate dsmr_notification 0007_support_for_telegram
./manage.py migrate dsmr_pvoutput 0002_pvoutput_latest_sync
./manage.py migrate dsmr_stats 0013_all_time_low
./manage.py migrate dsmr_weather 0006_schedule_weather_update
