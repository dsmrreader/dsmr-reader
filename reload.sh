#!/usr/bin/env bash


# Sending a HANGUP signal to Gunicorn's master process will gracefully reload its children.
echo ""
printf "%-50s" " * Reloading process: dsmr_webinterface (Gunicorn)"

if [ -f /tmp/gunicorn--dsmr_webinterface.pid ];
then
    cat /tmp/gunicorn--dsmr_webinterface.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [!!] PID file does not exist (as sudo user, try 'sudo supervisorctl start dsmr_webinterface')"
fi


# Management commands have some builtin mechanism for this as well.
printf "%-50s" " * Reloading process: dsmr_backend"
if [ -f /tmp/dsmrreader--dsmr_backend.pid ];
then
    cat /tmp/dsmrreader--dsmr_backend.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [!!] PID file does not exist (as sudo user, try 'sudo supervisorctl start dsmr_backend')"
fi


printf "%-50s" " * Reloading process: dsmr_datalogger"

if [ -f /tmp/dsmrreader--dsmr_datalogger.pid ];
then
    cat /tmp/dsmrreader--dsmr_datalogger.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [!!] PID file does not exist or the datalogger is disabled (Should it run? As sudo user, try 'sudo supervisorctl start dsmr_datalogger')"
fi
