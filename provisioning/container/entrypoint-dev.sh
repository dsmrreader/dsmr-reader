#!/bin/sh

# Trigger an error if non-zero exit code is encountered
set -e

# Only installs the current lock file state.
poetry install

# Playwright needs the browser build matching the locked version; a no-op when already present.
poetry run playwright install chromium

# This could collide if you happen to work on a migration yourself and you restart the container.
poetry run /app/src/manage.py migrate --noinput

# Reset password.
poetry run /app/src/manage.py dsmr_superuser

# E.g. "poetry run /app/src/manage.py runserver 8000"
echo "Running: ${@}"
exec ${@}
