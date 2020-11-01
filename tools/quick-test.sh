#!/usr/bin/env bash

ARGS=""

for CURRENT in "$@"
do
    ARGS="$ARGS $CURRENT"
done

echo ""
echo "--- Testing with SQLite (4 processes)..."
DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
export DJANGO_DATABASE_ENGINE
time pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test -n 2 $ARGS


echo ""
echo "--- Applying autopep8..."
./tools/apply-autopep8.sh


echo ""
echo "--- Running Pylama for code audit..."
pylama

# Abort when audit fails.
if [ $? -ne 0 ]; then
    echo "[!] Code audit failed [!]"
    exit;
fi

echo "OK"


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
