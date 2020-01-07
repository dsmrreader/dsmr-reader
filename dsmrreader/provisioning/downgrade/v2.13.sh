#!/bin/bash

# Dump for DSMR-reader v2.13
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0009_update_email_settings_mail_from
./manage.py migrate dsmr_backup 0007_remove_backupsettings_compress
./manage.py migrate dsmr_consumption 0012_add_voltage_indexes
./manage.py migrate dsmr_datalogger 0015_datalogger_foreign_countries
./manage.py migrate dsmr_frontend 0025_increase_max_dashboard_graph_width
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0012_mqtt_voltage_defaults
./manage.py migrate dsmr_notification 0007_support_for_telegram
./manage.py migrate dsmr_pvoutput 0002_pvoutput_latest_sync
./manage.py migrate dsmr_stats 0013_all_time_low
./manage.py migrate dsmr_weather 0006_schedule_weather_update