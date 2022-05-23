#!/usr/bin/env bash

CURRENT_DIR=$(cd `dirname $0` && pwd)

# Remove annoying PO headers that get regenerated every time. And sometimes they're empty, crashing the compiler.
echo "Dropping PO file meta data causing issues with VCS..."
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"PO-Revision-Date:/d'
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"POT-Creation-Date:/d'
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"X-Generator:/d'
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"Generated-By:/d'

# Same applies to the MO binaries. But since they're binaries we should NOT edit them.
# Just regenerate them AFTER we update the PO's.
echo "Generating MO files..."
$CURRENT_DIR/../manage.py compilemessages
