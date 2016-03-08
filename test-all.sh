#!/bin/bash

echo ""
echo "--- Testing with SQLite..."
./manage.py test --noinput --settings=dsmrreader.config.test_sqlite ### --with-coverage

echo ""
echo "--- Testing with PostgreSQL..."
./manage.py test --noinput --settings=dsmrreader.config.test_postgresql ### --with-coverage

echo ""
echo "--- Testing with MySQL..."
./manage.py test --noinput --settings=dsmrreader.config.test_mysql ### --with-coverage
