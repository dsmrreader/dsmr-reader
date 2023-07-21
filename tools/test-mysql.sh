#!/usr/bin/env bash


export DJANGO_SETTINGS_MODULE=dsmrreader.config.test


# Docker env vars take priority.
export DJANGO_DATABASE_HOST="${DOCKER_TEST_MYSQL_DJANGO_DATABASE_HOST:-127.0.0.1}"
export DJANGO_DATABASE_PORT="${DOCKER_TEST_MYSQL_DJANGO_DATABASE_PORT:-3306}"
export DJANGO_DATABASE_USER="${DOCKER_TEST_MYSQL_DJANGO_DATABASE_USER:-dsmrreader}"
export DJANGO_DATABASE_PASSWORD="${DOCKER_TEST_MYSQL_DJANGO_DATABASE_PASSWORD:-dsmrreader}"
export DJANGO_DATABASE_NAME="${DOCKER_TEST_MYSQL_DJANGO_DATABASE_NAME:-dsmrreader}"

echo ""
export DJANGO_DATABASE_ENGINE=django.db.backends.mysql
echo "--- Testing: $DJANGO_DATABASE_ENGINE"
poetry run pytest --cov --cov-report=term

if [ $? -ne 0 ]; then
    echo "[!] Tests failed: $DJANGO_DATABASE_ENGINE"
    exit 1;
fi


DIR=$(cd `dirname $0` && pwd)
sh $DIR/regenerate-translation-mo-files.sh
