#!/usr/bin/env bash

CURRENT_DIR=$(cd `dirname $0` && pwd)

export DJANGO_SETTINGS_MODULE=dsmrreader.config.test

echo ""
echo "--- Running tests for translations..."
export DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
poetry run pytest dsmr_frontend/tests/regression/test_translations.py


echo ""
echo "--- Clearing PO headers..."
sh $CURRENT_DIR/clear-po-headers.sh


echo ""
echo "--- Checking missing doc translations..."
cd $CURRENT_DIR/../docs/
poetry run sphinx-intl stat | grep -v "0 fuzzy, 0 untranslated" | grep -v changelog.po

if [ $? -ne 1 ]; then
    echo "[!] Pending documentation translations [!]"
    exit;
fi
