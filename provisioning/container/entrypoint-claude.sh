#!/bin/sh

# Trigger an error if non-zero exit code is encountered
set -e

# Only installs the current lock file state.
poetry install

echo "Running: ${@}"
exec ${@}
