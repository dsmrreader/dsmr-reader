#!/bin/bash
# 2.7.0 to 2.6.0

./manage.py migrate dsmr_frontend 0021_v260_release
./manage.py migrate dsmr_mqtt 0009_remove_optional_debug
