#!/bin/sh

# Trigger an error if non-zero exit code is encountered
set -e

# Seed Claude Code config from build template when bind mount is empty.
if [ -f /root/.claude.json.template ]; then
  CONTENT=$(cat /root/.claude.json 2>/dev/null || true)
  if [ -z "$CONTENT" ] || [ "$CONTENT" = "{}" ]; then
    cp /root/.claude.json.template /root/.claude.json
  fi
fi

# Only installs the current lock file state.
poetry install

# This could collide if you happen to work on a migration yourself and you restart the container.
poetry run /app/manage.py migrate --noinput

# Reset password.
poetry run /app/manage.py dsmr_superuser

# E.g. "poetry run /app/manage.py runserver 8000"
exec ${@}
