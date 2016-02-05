#!/bin/bash

echo "--- Testing with PostgreSQL..."
./manage.py test --settings=dsmrreader.config.test_postgresql -v2 --noinput

echo "--- Testing with MySQL..."
./manage.py test --settings=dsmrreader.config.test_mysql -v2 --noinput
