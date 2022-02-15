#!/usr/bin/env bash

# Dump for DSMR-reader v5.1.0
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0015_backend_restart_required
./manage.py migrate dsmr_backup 0014_dropbox_oauth
./manage.py migrate dsmr_consumption 0019_energy_supplier_price_decimals
./manage.py migrate dsmr_datalogger 0030_override_telegram_timestamp
./manage.py migrate dsmr_dropbox 0001_schedule_dropbox
./manage.py migrate dsmr_frontend 0045_frontendsettings_frontend_theme
./manage.py migrate dsmr_influxdb 0006_influxdb_settings_field_size
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0020_drop_mqtt_qos_setting
./manage.py migrate dsmr_notification 0008_dummy_notification_provider
./manage.py migrate dsmr_pvoutput 0004_pvoutput_setting_refactoring
./manage.py migrate dsmr_stats 0017_day_statistics_reading_history_retroactive
./manage.py migrate dsmr_weather 0006_schedule_weather_update
