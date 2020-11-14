#!/usr/bin/env bash
# Execute this script with "poetry run" or while in its shell.

export DJANGO_SETTINGS_MODULE=dsmrreader.config.test
export DJANGO_DATABASE_HOST=127.0.0.1
export DJANGO_DATABASE_USER=dsmrreader
export DJANGO_DATABASE_PASSWORD=dsmrreader
# Will be adjusted to 'test_*' by Django.
export DJANGO_DATABASE_NAME=dsmrreader


echo ""
export DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=term


echo ""
export DJANGO_DATABASE_ENGINE=django.db.backends.postgresql
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=term


#echo ""
#export DJANGO_DATABASE_ENGINE=django.db.backends.mysql
#echo "--- Testing: $DJANGO_DATABASE_ENGINE"
#pytest --cov --cov-report=term


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
