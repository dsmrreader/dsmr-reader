#!/bin/bash

echo "--- Testing with SQLite..."
./manage.py test --with-coverage --settings=dsmrreader.config.test --noinput

echo "--- Testing with PostgreSQL..."
./manage.py test --settings=dsmrreader.config.test_postgresql --noinput

echo "--- Testing with MySQL..."
./manage.py test --with-coverage --settings=dsmrreader.config.test_mysql --noinput
