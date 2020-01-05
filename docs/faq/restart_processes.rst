FAQ: Restarting application processes
=====================================

You might want or need to restart DSMR-reader manually at some time.
E.g.: Due to altered settings that need to be reapplied to the processes.

For a soft restart::

    # This only works if the processes already run.
    sudo su - dsmr
    ./reload.sh

For a hard restart::

    # Make sure you are root or sudo user.
    sudo supervisorctl restart all
