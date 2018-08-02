#!/bin/bash


echo ""
echo "--- Testing with SQLite (4 processes)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test.sqlite -n 4


echo ""
echo "--- Testing with PostgreSQL (4 processes)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test.postgresql -n 4


echo ""
echo "--- Testing with MySQL (1 process due to concurrency limitations)..."
pytest --pylama --cov --cov-report=html:coverage_report/html --cov-report=term --ds=dsmrreader.config.test.mysql


DIR=$(cd `dirname $0` && pwd)
sh $DIR/clear-po-headers.sh
