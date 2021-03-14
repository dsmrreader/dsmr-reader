Troubleshooting: Enable DEBUG logging
=====================================

DSMR-reader has DEBUG-logging, which makes the system log very verbosely about what it's trying to do.
This applies **specifically** to the ``dsmr_backend`` process.

.. note::

    Errors are likely to be logged at all times, no matter the DEBUG-logging level used. Debugging is only helpful to watch DSMR-reader's detailed behaviour.

The DEBUG-logging is disabled by default, to reduce writes on the filesystem. You can enable the logging by following these steps:

* Make sure you are ``dsmr`` user by executing::

    sudo su - dsmr

* Open the ``.env`` file and look for the code below::

    ### Logging level.
    ###DSMRREADER_LOGLEVEL=DEBUG

* Now remove the ``###`` from this line::

    ###DSMRREADER_LOGLEVEL=DEBUG

* It should now be::

    DSMRREADER_LOGLEVEL=DEBUG

* After editing the file, all processes need to be restarted to reflect the change. Go back to the **root user or sudoer** with::

    logout

* And restart::

    sudo supervisorctl restart all

* All done!
