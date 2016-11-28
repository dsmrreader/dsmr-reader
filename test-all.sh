#!/bin/bash

echo ""
echo "--- Testing with SQLite..."
pytest --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_sqlite 


echo ""
echo "--- Testing with PostgreSQL..."
pytest --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_postgresql


echo ""
echo "--- Testing with MySQL..."
pytest --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_mysql
