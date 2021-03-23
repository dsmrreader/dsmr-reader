Database: Resolving size warnings (PostgreSQL)
==============================================

You will need to reduce the amount of incoming data and also enable a data retention policy.

- First increase the datalogger sleep in the configuration panel. Make sure it's at least 5 or 10 seconds.
- Secondly, enable data retention policy in the configuration as well. A recommended setting is having DSMR-reader clean up data after a week or month.

After a few hours or days (depending on your hardware) the data should been reduced.
Depending on the amount of data deleted, you might want to execute a one-time ``vacuumdb`` afterwards. See below for more information.

Execute::

    sudo su - postgres
    vacuumdb -f -v -z -d dsmrreader
