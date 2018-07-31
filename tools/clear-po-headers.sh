#!/bin/bash


# Remove annoying headers that get regenerated every time.
sed -i '/"PO-Revision-Date:/d' dsmrreader/locales/nl/LC_MESSAGES/django.po
sed -i '/"POT-Creation-Date:/d' dsmrreader/locales/nl/LC_MESSAGES/django.po

sed -i '/"PO-Revision-Date:/d' docs/locale/nl/LC_MESSAGES/*.po
sed -i '/"POT-Creation-Date:/d' docs/locale/nl/LC_MESSAGES/*.po
