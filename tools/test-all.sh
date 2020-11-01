#!/usr/bin/env bash


echo ""
echo "--- Running Pylama for code audit..."
pylama

# Abort when audit fails.
if [ $? -ne 0 ]; then
    echo "[!] Code audit failed [!]"
    exit;
fi

echo "OK"


DJANGO_DATABASE_HOST=127.0.0.1
DJANGO_DATABASE_USER=dsmrreader
DJANGO_DATABASE_PASSWORD=dsmrreader
# Will be adjusted to 'test_*' by Django.
DJANGO_DATABASE_NAME=dsmrreader

export DJANGO_DATABASE_HOST
export DJANGO_DATABASE_USER
export DJANGO_DATABASE_PASSWORD
export DJANGO_DATABASE_NAME


echo ""
DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
export DJANGO_DATABASE_ENGINE
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test -n 2


echo ""
DJANGO_DATABASE_ENGINE=django.db.backends.postgresql
export DJANGO_DATABASE_ENGINE
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test -n 4


echo ""
DJANGO_DATABASE_ENGINE=django.db.backends.mysql
export DJANGO_DATABASE_ENGINE
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
