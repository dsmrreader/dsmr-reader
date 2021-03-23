Troubleshooting: Log files
==========================

DSMR-reader technically consists of these processes and they are watched by Supervisor:

+----------------+----------------------------------+
| Webinterface   | ``dsmr_webinterface``            |
+----------------+----------------------------------+
| Datalogger     | ``dsmr_datalogger``              |
+----------------+----------------------------------+
| Backend        | ``dsmr_backend``                 |
+----------------+----------------------------------+

You can view the status of all processes by running::

    sudo supervisorctl status

Any processes listed, should have the status ``RUNNING``. Stale or crashed processes can be restarted with::

    sudo supervisorctl restart <name>
    sudo supervisorctl restart dsmr_backend
    sudo supervisorctl restart ...

Or to restart them all simultaneously::

    sudo supervisorctl restart all


Each has its own log file(s):

+----------------+----------------------------------------------------------------------------------+
| Webinterface   | ``/var/log/supervisor/dsmr_webinterface.log``                                    |
+----------------+----------------------------------------------------------------------------------+
| Datalogger     | ``/var/log/supervisor/dsmr_datalogger.log``                                      |
+----------------+----------------------------------------------------------------------------------+
| Backend        | ``/var/log/supervisor/dsmr_backend.log``                                         |
+----------------+----------------------------------------------------------------------------------+

.. attention::

    The logfiles may be stale due to rotation. To see all logs for a process, try tailing a wildcard pattern, e.g.::

        sudo tail -f /var/log/supervisor/dsmr_webinterface*
        sudo tail -f /var/log/supervisor/dsmr_datalogger*
        sudo tail -f /var/log/supervisor/dsmr_backend*
