#!/usr/bin/env bash

# Dump for DSMR-reader v6.2.0
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0015_backend_restart_required
./manage.py migrate dsmr_backup 0017_backup_interval_in_days
./manage.py migrate dsmr_consumption 0021_schedule_quarter_hour_peaks_calculation
./manage.py migrate dsmr_datalogger 0033_fix_retention_intervals
./manage.py migrate dsmr_dropbox 0001_schedule_dropbox
./manage.py migrate dsmr_frontend 0051_alter_frontendsettings_electricity_delivered_alternate_color_and_more
./manage.py migrate dsmr_influxdb 0007_influxdb_api_url
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0022_alter_message_id
./manage.py migrate dsmr_notification 0008_dummy_notification_provider
./manage.py migrate dsmr_pvoutput 0004_pvoutput_setting_refactoring
./manage.py migrate dsmr_stats 0020_day_statistics_fix_total_gas_consumption_retroactive
./manage.py migrate dsmr_weather 0007_alter_weathersettings_buienradar_station
