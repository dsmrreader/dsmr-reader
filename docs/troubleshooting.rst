Troubleshooting
===============

.. contents::
    :depth: 2

.. note::

    If anything happens to fail or malfunction, please follow the steps below first to provide some background information when reporting an issue.


Log files
---------

Always start by checking the log files for errors.

DSMR-reader technically consists of these processes (some may or may not be used by you) and they are watched by Supervisor:

+----------------+----------------------------------+
| Webinterface   | ``dsmr_webinterface``            |
+----------------+----------------------------------+
| Datalogger     | ``dsmr_datalogger``              |
+----------------+----------------------------------+
| Backend        | ``dsmr_backend``                 |
+----------------+----------------------------------+

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


Supervisor
----------

You can view the status of all processes by running::

    sudo supervisorctl status

Any processes listed, should have the status ``RUNNING``. Stale or crashed processes can be restarted with::

    sudo supervisorctl restart <name>
    sudo supervisorctl restart dsmr_backend
    sudo supervisorctl restart ...

Or to restart them all simultaneously::

    sudo supervisorctl restart all


Debug info dump for Github issues
---------------------------------
You can supply additional debug info by executing the "**dsmr_debuginfo**" command and copying its output into your issue on Github.

.. note::

    The "**dsmr_debuginfo**" command is available since DSMR-reader v4.4 and higher.

Execute the following command::

    sudo su - dsmr
    ./manage.py dsmr_debuginfo

Copy its output to your Github issue.


Logging levels
--------------
If the processes do run, but you cannot find an error, (e.g.: things seem to hang or tend to be slow), there might be another issue at hand.

DSMR-reader has DEBUG-logging, which makes the system log very verbosely about what it's trying to do.
This applies **specifically** to the ``dsmr_backend`` process.

.. note::

    Errors are likely to be logged at all times, no matter the DEBUG-logging level used. Debugging is only helpful to watch DSMR-reader's detailed behaviour.

The DEBUG-logging is disabled by default, to reduce writes on the filesystem. You can enable the logging by following these steps:

* Make sure you are ``dsmr`` user by executing ``sudo su - dsmr``.
* Open the ``.env`` file and look for the code below::

    ### Logging level.
    ###DSMRREADER_LOGLEVEL=DEBUG

* Now remove the ``###`` from this line::

    ###DSMRREADER_LOGLEVEL=DEBUG

* It should now be::

    DSMRREADER_LOGLEVEL=DEBUG

* After editing the file, all processes need to be restarted. To do this, you can either execute::

    ./post-deploy.sh

* Or go back to the **sudo user** and execute::

    CTRL+D
    sudo supervisorctl restart all

* All done!


Unprocessed telegrams
---------------------
Are you experiencing lots of unprocessed telegrams? You may have excessive data stored, causing a drag in performance.
:doc:`More information can be found here<faq/data_throughput>`.


Contact
-------
Are you unable to resolve your problem or do you need any help?
:doc:`More information can be found here<contributing>`.
