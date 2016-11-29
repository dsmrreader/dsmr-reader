#!/bin/bash

echo ""
echo "--- Running Pylama for code audit..."
pylama

echo ""
echo "--- Testing with SQLite (4 processes)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_sqlite -n 4


echo ""
echo "--- Testing with PostgreSQL (4 processes)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_postgresql -n 4


echo ""
echo "--- Testing with MySQL (1 proces due to concurrency limitations)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_mysql
