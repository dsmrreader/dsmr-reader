#!/usr/bin/env bash

# Dump for DSMR-reader v4.1.1
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0015_backend_restart_required
./manage.py migrate dsmr_backup 0011_remove_backupsettings_latest_backup
./manage.py migrate dsmr_consumption 0015_track_power_current
./manage.py migrate dsmr_datalogger 0026_datalogger_restart_required
./manage.py migrate dsmr_frontend 0040_v4_1_0_release
./manage.py migrate dsmr_influxdb 0004_client_settings_update
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0016_client_settings_update
./manage.py migrate dsmr_notification 0007_support_for_telegram
./manage.py migrate dsmr_pvoutput 0002_pvoutput_latest_sync
./manage.py migrate dsmr_stats 0014_day_total_cost_index
./manage.py migrate dsmr_weather 0006_schedule_weather_update
