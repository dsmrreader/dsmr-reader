#!/usr/bin/env bash

# Dump for DSMR-reader v4.8
./manage.py migrate dsmr_api 0003_create_api_user
./manage.py migrate dsmr_backend 0015_backend_restart_required
./manage.py migrate dsmr_backup 0012_increase_dropbox_token_length
./manage.py migrate dsmr_consumption 0018_allow_inversed_fixed_costs
./manage.py migrate dsmr_datalogger 0029_default_retention_to_month
./manage.py migrate dsmr_frontend 0043_default_color_update_tariff_2
./manage.py migrate dsmr_influxdb 0004_client_settings_update
./manage.py migrate dsmr_mindergas 0005_schedule_mindergas_export
./manage.py migrate dsmr_mqtt 0018_mqtt_always_reconnect
./manage.py migrate dsmr_notification 0008_dummy_notification_provider
./manage.py migrate dsmr_pvoutput 0002_pvoutput_latest_sync
./manage.py migrate dsmr_stats 0015_fixed_daily_cost
./manage.py migrate dsmr_weather 0006_schedule_weather_update
