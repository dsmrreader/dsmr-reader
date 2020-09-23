#!/bin/bash

CURRENT_DIR=$(cd `dirname $0` && pwd)
cd $CURRENT_DIR/../

autopep8 -r . --in-place
