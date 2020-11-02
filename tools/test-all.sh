#!/usr/bin/env bash


DJANGO_SETTINGS_MODULE=dsmrreader.config.test
DJANGO_DATABASE_HOST=127.0.0.1
DJANGO_DATABASE_USER=dsmrreader
DJANGO_DATABASE_PASSWORD=dsmrreader
# Will be adjusted to 'test_*' by Django.
DJANGO_DATABASE_NAME=dsmrreader

export DJANGO_SETTINGS_MODULE
export DJANGO_DATABASE_HOST
export DJANGO_DATABASE_USER
export DJANGO_DATABASE_PASSWORD
export DJANGO_DATABASE_NAME


echo ""
DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
export DJANGO_DATABASE_ENGINE
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=html --cov-report=term -n 2


echo ""
DJANGO_DATABASE_ENGINE=django.db.backends.postgresql
export DJANGO_DATABASE_ENGINE
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=html --cov-report=term -n 4


echo ""
DJANGO_DATABASE_ENGINE=django.db.backends.mysql
export DJANGO_DATABASE_ENGINE
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=html --cov-report=term dsmr_api/tests/v1/test_api.py


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
