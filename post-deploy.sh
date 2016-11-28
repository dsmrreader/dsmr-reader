#!/bin/bash

echo ""
echo ""
echo " --- Checking & synchronizing base requirements for changes."
pip3 install -r dsmrreader/provisioning/requirements/base.txt


echo ""
echo ""
echo " --- Checking & synchronizing database changes/migrations."
./manage.py migrate --noinput


echo ""
echo ""
echo " --- Checking & synchronizing static file changes."
./manage.py collectstatic --noinput


echo ""
echo ""
echo " --- Reloading app code..."


# Sending a HANGUP signal to Gunicorn's master process will gracefully reload its children.
echo ""
echo " * Reloading Gunicorn (webinterface)..."

if [ -f /var/tmp/gunicorn--dsmr_webinterface.pid ];
then
    cat /var/tmp/gunicorn--dsmr_webinterface.pid | xargs kill -HUP
    echo " [x] Done!"
else
    echo " !-- PID file does not exist (yet)"
fi


# Management commands have some builtin mechanism as well for this.
echo ""
echo " * Reloading backend process..."
if [ -f /var/tmp/dsmrreader--dsmr_backend.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_backend.pid | xargs kill -HUP
    echo " [x] Done!"
else
    echo " !-- PID file does not exist (yet)"
fi


echo ""
echo " * Reloading datalogger process..."

if [ -f /var/tmp/dsmrreader--dsmr_datalogger.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_datalogger.pid | xargs kill -HUP
    echo " [x] Done!"
else
    echo " !-- PID file does not exist (yet)"
fi


echo ""
echo ""
echo " --- Clearing cache..."
./manage.py dsmr_frontend_clear_cache
