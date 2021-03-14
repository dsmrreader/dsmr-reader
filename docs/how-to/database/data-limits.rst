Data limits
===========

By default DSMR-reader reads and preserves all telegram data read.

When using a Raspberry Pi (or similar) combined with a DSMR version 5 smart meter (the default nowadays), you may experience issues after a while.

This is caused by the high data throughput of DSMR version 5, which produces a new telegram every second.
Both DSMR-reader and most of its users do not need this high frequency of telegrams to store, calculate and plot consumption data.

Therefor two measures can be taken: Increasing datalogger sleep and data retention policy.


How can I increase the datalogger sleep time?
---------------------------------------------

Increase the datalogger sleep time :doc:`in the configuration</tutorial/configuration>` to 5 seconds or higher.
This will save a lot of disk storage, especially when using a Raspberry Pi SD card, usually having a size of 16 GB max.


How can I configure a data retention policy?
--------------------------------------------

Configure a data retention policy :doc:`in the configuration</tutorial/configuration>`.
This will eventually delete up to 99 percent of the telegrams, always preserving a few historically.
Also, day and hour totals are **never** deleted by retention policies.


.. attention::::

    New installations of DSMR-reader ``v4.1`` or higher will start with a default retention policy of one month.
