#!/usr/bin/env bash

CURRENT_DIR=$(cd `dirname $0` && pwd)


# Remove annoying headers that get regenerated every time. And sometimes they're empty, crashing the compiler.
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"PO-Revision-Date:/d'
find $CURRENT_DIR/../ -type f -iname '*.po' | xargs sed -i '/"POT-Creation-Date:/d'
