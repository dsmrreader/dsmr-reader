#!/usr/bin/env bash

CURRENT_DIR=$(cd `dirname $0` && pwd)

echo "Dropping meta data causing issues with VCS..."

# Remove annoying PO headers that get regenerated every time. And sometimes they're empty, crashing the compiler.
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"PO-Revision-Date:/d'
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"POT-Creation-Date:/d'

# These also update PO once every while, causing a lot of issues in VCS, which is quite annoying.
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"X-Generator:/d'
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"Generated-By:/d'

# Same applies to the MO binaries.
find $CURRENT_DIR/../ -type f -iname '*.mo' | xargs sed -i '/PO-Revision-Date:/d'
find $CURRENT_DIR/../ -type f -iname '*.mo' | xargs sed -i '/POT-Creation-Date:/d'
find $CURRENT_DIR/../ -type f -iname '*.mo' | xargs sed -i '/X-Generator:/d'
find $CURRENT_DIR/../ -type f -iname '*.mo' | xargs sed -i '/Generated-By:/d'
