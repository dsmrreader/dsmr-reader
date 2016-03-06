#!/bin/bash

echo ""
echo " --- Pulling remote repository for new commits..."
git fetch
echo ""

echo " --- The following changes will be applied (if any)."
git log ..origin/master
echo ""

echo " --- Merging/updating checkout."
git merge FETCH_HEAD
echo ""

echo ""
echo " --- Checking & synchronizing base requirements for changes."
pip3 install -r dsmrreader/provisioning/requirements/base.txt

echo ""
echo " --- Checking & synchronizing database changes/migrations."
./manage.py migrate --noinput

echo ""
echo " --- Checking & synchronizing static file changes."
./manage.py collectstatic --noinput

echo ""
echo " --- Sending an SIGHUP to supervisor processes to gracefully reload itself."
./reload.sh

echo ""
echo " --- Clearing cache..."
./manage.py dsmr_frontend_clear_cache

echo ""
echo " >>> Deployment complete! Please check whether all your Supervisor processes are still up & running! <<<"
