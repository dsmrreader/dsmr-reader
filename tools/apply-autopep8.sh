#!/usr/bin/env bash
# Execute this script with "poetry run" or while in its shell.

CURRENT_DIR=$(cd `dirname $0` && pwd)
cd $CURRENT_DIR/../


autopep8 -r . --in-place
