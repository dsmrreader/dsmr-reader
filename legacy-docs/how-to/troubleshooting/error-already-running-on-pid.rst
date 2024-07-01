Common error resolution: How do I fix ``Error: Already running on PID 1234``?
=============================================================================

If you're seeing this error::

    Error: Already running on PID 1234 (or pid file '/tmp/gunicorn--dsmr_webinterface.pid' is stale)

Just delete the PID file and restart the webinterface::

    sudo rm /tmp/gunicorn--dsmr_webinterface.pid
    sudo supervisorctl restart dsmr_webinterface
