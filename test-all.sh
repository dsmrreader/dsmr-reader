#!/bin/bash

echo ""
echo "--- Running Pylama for code audit..."
pylama

echo ""
echo "--- Testing with SQLite..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_sqlite 


echo ""
echo "--- Testing with PostgreSQL..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_postgresql


echo ""
echo "--- Testing with MySQL..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test_mysql
