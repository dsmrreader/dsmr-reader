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
pytest --cov --cov-report=html --cov-report=term $ARGS

if [ $? -ne 0 ]; then
    echo "[!] Tests failed [!]"
    exit;
fi


echo ""
echo "--- Applying autopep8..."
./tools/apply-autopep8.sh


echo ""
echo "--- Running Pylama for code audit..."
pylama

if [ $? -ne 0 ]; then
    echo "[!] Code audit failed [!]"
    exit;
fi


echo ""
echo "--- Clearing PO headers..."
sh $CURRENT_DIR/clear-po-headers.sh


echo ""
echo "--- Checking missing doc translations..."
cd $CURRENT_DIR/../docs/
sphinx-intl stat | grep -v "0 fuzzy, 0 untranslated" | grep -v changelog.po

if [ $? -ne 1 ]; then
    echo "[!] Pending documentation translations [!]"
    exit;
fi
