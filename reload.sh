#!/bin/bash


# Sending a HANGUP signal to Gunicorn's master process will gracefully reload its children.
echo ""
printf "%-50s" " * Reloading process: dsmr_webinterface (Gunicorn)"

if [ -f /var/tmp/gunicorn--dsmr_webinterface.pid ];
then
    cat /var/tmp/gunicorn--dsmr_webinterface.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [??] PID file does not exist (as sudo user try 'sudo supervisorctl start dsmr_webinterface')"
fi


# Management commands have some builtin mechanism for this as well.
printf "%-50s" " * Reloading process: dsmr_backend"
if [ -f /var/tmp/dsmrreader--dsmr_backend.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_backend.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [??] PID file does not exist (as sudo user try 'sudo supervisorctl start dsmr_backend')"
fi


printf "%-50s" " * Reloading process: dsmr_datalogger"

if [ -f /var/tmp/dsmrreader--dsmr_datalogger.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_datalogger.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [??] PID file does not exist (as sudo user try 'sudo supervisorctl start dsmr_datalogger')"
fi


printf "%-50s" " * Reloading process: dsmr_client"

if [ -f /var/tmp/dsmrreader--dsmr_client.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_client.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [??] PID file does not exist (as sudo user try 'sudo supervisorctl start dsmr_client')"
fi
