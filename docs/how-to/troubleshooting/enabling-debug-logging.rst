Troubleshooting: Enable DEBUG logging
=====================================

DSMR-reader has DEBUG logging, which makes the system log very verbosely about what it's trying to do and **why** it executes or skips certain actions.

This applies **specifically** to the ``dsmr_backend`` process and its log.

.. tip::

    Errors are likely to be logged at all times, no matter the logging level used.
    DEBUG logging is only helpful to watch DSMR-reader's detailed behaviour, when debugging issues.

    The DEBUG logging is **disabled by default**, to reduce the number writes on the filesystem.

.. caution::

    Don't forget to disable DEBUG logging whenever you are done debugging.

You can enable the DEBUG logging by setting the ``DSMRREADER_LOGLEVEL`` env var to ``DEBUG``. Follow these steps:

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

.. seealso::

    :doc:`See here for where to find the log files </how-to/troubleshooting/logfiles>`.
