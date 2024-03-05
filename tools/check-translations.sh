#!/usr/bin/env sh

CURRENT_DIR=$(cd `dirname $0` && pwd)

export DJANGO_SETTINGS_MODULE=dsmrreader.config.test

echo ""
echo "--- Running tests for translations..."
export DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
poetry run pytest dsmr_frontend/tests/regression/test_translations.py


echo ""
echo "--- Listing untranslated files..."
poetry run sphinx-intl stat -d dsmrreader/locales/ -d docs/_locale/ | grep -v "0 fuzzy, 0 untranslated" | grep -v changelog.po

if [ $? -ne 1 ]; then
    echo "[!] Pending translations [!]"
    poetry run sphinx-intl stat -d dsmrreader/locales/ -d docs/_locale/ | grep -v "0 fuzzy, 0 untranslated" | grep -v changelog.po
    exit 1;
fi
