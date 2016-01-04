#!/bin/sh

##################################################################################################
### Creates a daily MYSQL database backup at the $DIRECTORY location below.
###
### COPY this file and schedule it daily by root user, do not symlink!
###
### Howto: Place a file in /etc/cron.daily/database-backup, only containing these two lines:
### (asumes you copied the script to '/root/mysql-backup.sh' in this example)
###
### 	#!/bin/sh
### 	/root/mysql-backup.sh
###
### VERIFY your cronjob and its result once by executing: run-parts -v /etc/cron.daily
##################################################################################################

DIRECTORY="/data"
DATABASE="dsmrreader"
DAY=$(date +"%A")
FILE="$DIRECTORY/backup-mysql-$DAY.sql.gz"

echo " --- Dumping backup of '$DATABASE' to: $FILE"

if [ ! -d "$DIRECTORY" ]; then
  mkdir -p $DIRECTORY -m 0700
fi

# Note: The backup itself is executed by postgres user, but writing the file by root.
mysqldump --defaults-file=/etc/mysql/debian.cnf $DATABASE -v --extended-insert --lock-all-tables --hex-blob | gzip --fast > $FILE
ls -lh $FILE
