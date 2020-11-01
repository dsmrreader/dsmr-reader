#!/usr/bin/env bash

CURRENT_DIR=$(cd `dirname $0` && pwd)


# Remove annoying headers that get regenerated every time. And sometimes they're empty, crashing the compiler.
sed -i '/"PO-Revision-Date:/d' $CURRENT_DIR/../dsmrreader/locales/nl/LC_MESSAGES/django.po
sed -i '/"POT-Creation-Date:/d' $CURRENT_DIR/../dsmrreader/locales/nl/LC_MESSAGES/django.po

sed -i '/"PO-Revision-Date:/d' $CURRENT_DIR/../docs/locale/nl/LC_MESSAGES/*.po
sed -i '/"POT-Creation-Date:/d' $CURRENT_DIR/../docs/locale/nl/LC_MESSAGES/*.po

sed -i '/"PO-Revision-Date:/d' $CURRENT_DIR/../docs/locale/nl/LC_MESSAGES/*/*.po
sed -i '/"POT-Creation-Date:/d' $CURRENT_DIR/../docs/locale/nl/LC_MESSAGES/*/*.po
