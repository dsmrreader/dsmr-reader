#!/bin/bash

# Sending a HANGUP signal to Gunicorn's master process will gracefully reload its children.
cat /var/tmp/gunicorn--dsmr_webinterface.pid | xargs kill -HUP
echo "Reloaded Gunicorn process running the webinterface. Other processes will be reloaded automatically on next run."
