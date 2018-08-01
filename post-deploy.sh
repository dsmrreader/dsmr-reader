#!/bin/bash

echo ""
echo ""
echo " --- Checking whether VirtualEnv is activated."
python -c 'import sys; exit_code = 0 if hasattr(sys, "real_prefix") else 1; sys.exit(exit_code);'

if [ $? -ne 0 ]; then
    echo "     [i] ----- Activating 'dsmrreader' VirtualEnv..."
    source ~/.virtualenvs/dsmrreader/bin/activate
    
    if [ $? -ne 0 ]; then
        echo "     [!] FAILED to switch to 'dsmrreader' VirtualEnv (is it installed?)"
        exit;
    fi
fi


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
printf "%-50s" " * Reloading process: dsmr_webinterface (Gunicorn)"

if [ -f /var/tmp/gunicorn--dsmr_webinterface.pid ];
then
    cat /var/tmp/gunicorn--dsmr_webinterface.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [FAILED] PID file does not exist! (yet?)"
fi


# Management commands have some builtin mechanism as well for this.
printf "%-50s" " * Reloading process: dsmr_backend"
if [ -f /var/tmp/dsmrreader--.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_backend.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [FAILED] PID file does not exist! (yet?)"
fi


printf "%-50s" " * Reloading process: dsmr_datalogger"

if [ -f /var/tmp/dsmrreader--dsmr_datalogger.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_datalogger.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [FAILED] PID file does not exist! (yet?)"
fi


printf "%-50s" " * Reloading process: dsmr_mqtt"

if [ -f /var/tmp/dsmrreader--dsmr_mqtt.pid ];
then
    cat /var/tmp/dsmrreader--dsmr_mqtt.pid | xargs kill -HUP
    echo "   [OK]"
else
    echo "   [FAILED] PID file does not exist! (yet?)"
fi


echo ""
echo ""
echo " --- Clearing cache..."
./manage.py dsmr_frontend_clear_cache
