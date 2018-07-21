#!/bin/bash


ARGS=""

for CURRENT in "$@"
do
    ARGS="$ARGS $CURRENT"
done


echo ""
echo "--- Testing with SQLite (4 processes)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test.sqlite -n 4 $ARGS


# Remove annoying headers that get regenerated every time.
sed -i '/"PO-Revision-Date:/d' dsmrreader/locales/nl/LC_MESSAGES/django.po
sed -i '/"POT-Creation-Date:/d' dsmrreader/locales/nl/LC_MESSAGES/django.po

sed -i '/"PO-Revision-Date:/d' docs/locale/nl/LC_MESSAGES/*.po
sed -i '/"POT-Creation-Date:/d' docs/locale/nl/LC_MESSAGES/*.po
