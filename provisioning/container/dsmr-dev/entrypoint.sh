#!/bin/sh

# Trigger an error if non-zero exit code is encountered
set -e

poetry install
poetry run /app/manage.py migrate --noinput

# E.g. "poetry run /app/manage.py runserver 8000"
exec ${@}
