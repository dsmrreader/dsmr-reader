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


echo ""
echo "--- Testing with SQLite (4 processes)..."
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test.sqlite -n 4


echo ""
echo "--- Testing with PostgreSQL (4 processes)..."
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test.postgresql -n 4


echo ""
echo "--- Testing with MySQL (1 process due to concurrency limitations)..."
pytest --cov --cov-report=html --cov-report=term --ds=dsmrreader.config.test.mysql


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
