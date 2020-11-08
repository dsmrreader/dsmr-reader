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


# Remove annoying header with datetime diffs.
sh $CURRENT_DIR/clear-po-headers.sh


# Check missing doc translations.
cd $CURRENT_DIR/../docs/
sphinx-intl stat | grep -v "0 fuzzy, 0 untranslated" | grep -v changelog.po

if [ $? -ne 1 ]; then
    echo "[!] Pending documentation translations [!]"
    exit;
fi

cd $CURRENT_DIR
