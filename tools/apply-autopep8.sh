#!/usr/bin/env bash

CURRENT_DIR=$(cd `dirname $0` && pwd)
cd $CURRENT_DIR/../

poetry run autopep8 -r . --in-place
