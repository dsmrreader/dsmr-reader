#!/usr/bin/env bash

CURRENT_DIR=$(cd `dirname $0` && pwd)
ARGS=""

for CURRENT in "$@"
do
    ARGS="$ARGS $CURRENT"
done


export DJANGO_SETTINGS_MODULE=dsmrreader.config.test

echo ""
echo "--- Testing with SQLite..."
export DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
#poetry run pytest --cov --cov-report=html --cov-report=term $ARGS
poetry run pytest --cov --cov-report=html $ARGS

if [ $? -ne 0 ]; then
    echo "[!] Tests failed [!]"
    exit 1;
fi


echo ""
echo "--- Applying autopep8..."
poetry run autopep8 -r . --in-place


echo ""
echo "--- Running flake8..."
poetry run flake8

if [ $? -ne 0 ]; then
    echo "[!] Failure"
    exit 1;
fi


echo ""
echo "--- Running safety (insecure packages check)..."
poetry run safety check --bare

if [ $? -ne 0 ]; then
    echo "[!] Failure"
    exit 1;
fi


echo ""
echo "--- Running Pylama for code audit..."
poetry run pylama

if [ $? -ne 0 ]; then
    echo "[!] Failure"
    exit 1;
fi


echo ""
echo ">>> Ensure to run 'Check translations' manually, when required..."
