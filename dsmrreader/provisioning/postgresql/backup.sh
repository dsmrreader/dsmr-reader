#!/bin/sh
DAY=$(date +"%A")
FILE="/data/backup-postgres-$DAY.sql.gz"
sudo -u postgres pg_dump -d dsmrreader -v | gzip --fast > $FILE
ls -lh $FILE
