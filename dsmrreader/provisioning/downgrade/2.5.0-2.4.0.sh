#!/bin/bash
# 2.5.0 to 2.4.0

./manage.py migrate dsmr_datalogger 0011_raw_telegram_insight
./manage.py migrate dsmr_consumption 0010_phases_currently_returned
./manage.py migrate dsmr_mqtt 0008_mqtt_null_payload
