#!/bin/bash


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

# Management commands have some mechanisme builtin as well for this.
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
