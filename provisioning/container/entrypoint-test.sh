#!/bin/sh

# Trigger an error if non-zero exit code is encountered
set -e

poetry install

# Playwright needs the browser build matching the locked version; a no-op when already present.
poetry run playwright install chromium

echo "Running: ${@}"
exec ${@}
