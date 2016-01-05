#!/bin/bash

echo ""
echo " --- Checking remote repository for new commits."
hg pull --up

echo ""
echo " --- Checking & synchronizing base requirements for changes."
pip3 install -r dsmrreader/provisioning/requirements/base.txt

echo ""
echo " --- Checking & synchronizing static file changes."
./manage.py collectstatic --noinput

echo ""
echo " --- Checking & synchronizing database changes/migrations."
./manage.py migrate

echo ""
echo " --- Sending an SIGHUP to Gunicorn process to gracefully reload itself (webinterface)."
./reload.sh

echo ""
echo " >>> Deployment complete! Please check whether all your Supervisor processes are still up & running! <<<"