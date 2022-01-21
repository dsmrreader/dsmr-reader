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
poetry run pytest --cov --cov-report=html --cov-report=term $ARGS

if [ $? -ne 0 ]; then
    echo "[!] Tests failed [!]"
    exit 1;
fi


echo ""
echo "--- Applying autopep8..."
poetry run autopep8 -r . --in-place


echo ""
echo "--- Running Pylama for code audit..."
poetry run pylama

if [ $? -ne 0 ]; then
    echo "[!] Code audit failed [!]"
    exit 1;
fi


echo ""
echo "--- Clearing PO headers..."
sh $CURRENT_DIR/clear-po-headers.sh


echo ""
echo "--- Checking missing translations..."
poetry run sphinx-intl stat -d dsmrreader/locales/ -d docs/_locale/ | grep -v "0 fuzzy, 0 untranslated" | grep -v changelog.po

if [ $? -ne 1 ]; then
    echo "[!] Pending translations [!]"
    poetry run sphinx-intl stat -d dsmrreader/locales/ -d docs/_locale/ | grep -v "0 fuzzy, 0 untranslated" | grep -v changelog.po
    exit 1;
fi
