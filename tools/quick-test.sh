#!/bin/bash


ARGS=""

for CURRENT in "$@"
do
    ARGS="$ARGS $CURRENT"
done


echo ""
echo "--- Testing with SQLite (4 processes)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test.sqlite -n 4 $ARGS


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
