Restarting DSMR-reader processes
================================

You might want to restart DSMR-reader manually, due to changed settings that need to re-apply.

For a soft restart::

    sudo su - dsmr
    ./reload.sh

For a hard restart::

    sudo supervisorctl restart all
