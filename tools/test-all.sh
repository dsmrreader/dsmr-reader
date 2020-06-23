#!/bin/bash


echo ""
echo "--- Running Pylama for code audit..."
pylama

# Abort when audit fails.
if [ $? -ne 0 ]; then
    echo "[!] Code audit failed [!]"
    exit;
fi

echo "OK"


DB_HOST=127.0.0.1
DB_USER=dsmrreader
DB_PASS=dsmrreader
# Will be adjusted to 'test_*' by Django.
DB_NAME=dsmrreader

export DB_HOST
export DB_USER
export DB_PASS
export DB_NAME


echo ""
echo "--- Testing with SQLite (4 processes)..."
DB_ENGINE=django.db.backends.sqlite3
export DB_ENGINE
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test -n 2


echo ""
echo "--- Testing with PostgreSQL (4 processes)..."
DB_ENGINE=django.db.backends.postgresql
export DB_ENGINE
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test -n 4


echo ""
echo "--- Testing with MySQL (1 process due to concurrency limitations)..."
DB_ENGINE=django.db.backends.mysql
export DB_ENGINE
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
