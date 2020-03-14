#!/bin/bash

# Dump for DSMR-reader v3.7
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0014_verbose_field_translations
./manage.py migrate dsmr_backup 0009_compression_level
./manage.py migrate dsmr_consumption 0015_track_power_current
./manage.py migrate dsmr_datalogger 0021_schedule_retention_data_rotation
./manage.py migrate dsmr_frontend 0034_mysql_timezone_support
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0014_mqtt_telegram_defaults
./manage.py migrate dsmr_notification 0007_support_for_telegram
./manage.py migrate dsmr_pvoutput 0002_pvoutput_latest_sync
./manage.py migrate dsmr_stats 0014_day_total_cost_index
./manage.py migrate dsmr_weather 0006_schedule_weather_update
