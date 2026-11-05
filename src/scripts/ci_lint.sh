#!/bin/sh

# Runs all static checks in a single container run, as the test entrypoint has a fixed startup cost.
set -e

poetry run black --check .
poetry run djlint --check .
poetry run flake8 -v
poetry run mypy /app/src
