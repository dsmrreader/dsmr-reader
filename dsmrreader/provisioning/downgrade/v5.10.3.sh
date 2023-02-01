#!/usr/bin/env bash

# Dump for DSMR-reader v5.10.3
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0015_backend_restart_required
./manage.py migrate dsmr_backup 0017_backup_interval_in_days
./manage.py migrate dsmr_consumption 0021_schedule_quarter_hour_peaks_calculation
./manage.py migrate dsmr_datalogger 0032_dsmr_extra_device_channel
./manage.py migrate dsmr_dropbox 0001_schedule_dropbox
./manage.py migrate dsmr_frontend 0049_alter_notification_options
./manage.py migrate dsmr_influxdb 0006_influxdb_settings_field_size
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0021_quarter_hour_peak_mqtt
./manage.py migrate dsmr_notification 0008_dummy_notification_provider
./manage.py migrate dsmr_pvoutput 0004_pvoutput_setting_refactoring
./manage.py migrate dsmr_stats 0020_day_statistics_fix_total_gas_consumption_retroactive
./manage.py migrate dsmr_weather 0006_schedule_weather_update
