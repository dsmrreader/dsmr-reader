#!/bin/sh

# Trigger an error if non-zero exit code is encountered
set -e

# Automatically check and install. Will also work with changed Python versions in the container.
#poetry update

# This could collide if you happen to work on a migration yourself and you restart the container.
poetry run /app/manage.py migrate --noinput

# Reset password.
poetry run /app/manage.py dsmr_superuser

# E.g. "poetry run /app/manage.py runserver 8000"
exec ${@}
