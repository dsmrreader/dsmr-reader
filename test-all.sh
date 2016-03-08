#!/bin/bash

echo ""
echo "--- Testing with SQLite..."
./manage.py test --noinput --with-coverage --settings=dsmrreader.config.test_sqlite

echo ""
echo "--- Testing with PostgreSQL..."
./manage.py test --noinput --with-coverage --settings=dsmrreader.config.test_postgresql

echo ""
echo "--- Testing with MySQL..."
./manage.py test --noinput --with-coverage --settings=dsmrreader.config.test_mysql
