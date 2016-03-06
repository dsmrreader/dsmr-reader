#!/bin/bash

# Sending a HANGUP signal to Gunicorn's master process will gracefully reload its children.
echo " * Reloading Gunicorn (webinterface)..."
cat /var/tmp/gunicorn--dsmr_webinterface.pid | xargs kill -HUP

# Management commands have some mechanisme builtin as well for this.
echo " * Reloading backend process..."
cat /var/tmp/dsmrreader--dsmr_backend.pid | xargs kill -HUP

echo " * Reloading datalogger process..."
cat /var/tmp/dsmrreader--dsmr_datalogger.pid | xargs kill -HUP

echo " --- Done!"
