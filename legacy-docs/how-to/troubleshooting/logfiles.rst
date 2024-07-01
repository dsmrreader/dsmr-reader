Troubleshooting: Log files
==========================

DSMR-reader technically consists of these processes and they are watched by Supervisor:

+----------------+-----------------------+------------------------------------------------------------+
| **Backend**    | ``dsmr_backend``      | Most important process, handles all background processing. |
+----------------+-----------------------+------------------------------------------------------------+
| Datalogger     | ``dsmr_datalogger``   | Local datalogger reading telegrams (if used).              |
+----------------+-----------------------+------------------------------------------------------------+
| Webinterface   | ``dsmr_webinterface`` | Hosts the GUI of DSMR-reader                               |
+----------------+-----------------------+------------------------------------------------------------+

You can view the status of all processes by running::

    sudo supervisorctl status


Any processes listed, should have the status ``RUNNING``. Stale or crashed processes can be restarted with::

    sudo supervisorctl restart <name>
    sudo supervisorctl restart dsmr_backend
    sudo supervisorctl restart ...


Or to restart them all simultaneously::

    sudo supervisorctl restart all


Each has its own log file(s):

+----------------+-----------------------------------------------+
| Backend        | ``/var/log/supervisor/dsmr_backend.log``      |
+----------------+-----------------------------------------------+
| Datalogger     | ``/var/log/supervisor/dsmr_datalogger.log``   |
+----------------+-----------------------------------------------+
| Webinterface   | ``/var/log/supervisor/dsmr_webinterface.log`` |
+----------------+-----------------------------------------------+

By default, only errors are logged. You can enable DEBUG logging which will make the backend log greatly more verbose.

.. seealso::

    :doc:`See here for how to enable DEBUG logging </how-to/troubleshooting/enabling-debug-logging>`.


.. attention::

    The logfiles may be stale due to rotation. To see all logs for a process, try tailing a wildcard pattern, e.g.::

        sudo tail -f /var/log/supervisor/dsmr_webinterface*
        sudo tail -f /var/log/supervisor/dsmr_datalogger*
        sudo tail -f /var/log/supervisor/dsmr_backend*
