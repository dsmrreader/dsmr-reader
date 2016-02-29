#!/bin/bash

echo "--- Testing with SQLite..."
./manage.py test --settings=dsmrreader.config.test --noinput --with-coverage

echo "--- Testing with PostgreSQL..."
# See issue #62 @ Github.
./manage.py test --settings=dsmrreader.config.test_postgresql --noinput

echo "--- Testing with MySQL..."
./manage.py test --settings=dsmrreader.config.test_mysql --noinput --with-coverage
