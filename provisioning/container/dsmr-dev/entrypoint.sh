#!/bin/sh

# Trigger an error if non-zero exit code is encountered
set -e

poetry install -v

# E.g. "runserver"
exec ${@}
