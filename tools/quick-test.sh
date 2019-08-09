#!/bin/bash

ARGS=""

for CURRENT in "$@"
do
    ARGS="$ARGS $CURRENT"
done


echo ""
echo "--- Testing with SQLite (4 processes)..."
time pytest --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test.sqlite -n 2 $ARGS


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
