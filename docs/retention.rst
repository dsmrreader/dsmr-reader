Retention
=========

By default all DSMR-readings read by of sent to the application are stored indefinitely.
DSMR v5 smart meters allow DSMR-readings to be recorded every second, resulting in over 30 million readings each year. 

Eventually this **will cause degraded performance** in the application/database and for that reason you might want to apply retention to this data. 
Please note that enabling this feature will **not discard all readings**, as it will **preserve the first and last reading of each hour**.

.. contents::


Notes / warnings
----------------
* The application will **slowly** apply retention **during night**, cleaning up a maximum of 24 hours worth of data on each backend run executed.

* Enabling retention will prevent you from regenerating past day statistics with different prices (due to loss of accuracy).

* PostgreSQL does not free up unused disk space immediately. If you've enabled retention for the first time, make sure to run the following command once after a few days::

    # Switch to PostgreSQL user.
    sudo su - postgres
    
    # This may take a while and slow your application, depending on your database size!
    vacuumdb -a -f -v



How to enable
-------------

The admin configuration has a section called "Retention configuration". 
You can specify whether you want retention at all and set the lifetime of the data being stored. 


Data affected
-------------

DSMR-readings
~~~~~~~~~~~~~
The source of all data. It is, however, only read and processed once, so it can be discarded safely after processing.

Electricity Consumption
~~~~~~~~~~~~~~~~~~~~~~~
This is aggregated data either created from a single DSMR-reader or a minute worth of DSMR-readings, depending on whether you've enabled grouping.

Gas Consumption
~~~~~~~~~~~~~~~
This data type is aggregated from any differences in 'extra device timestamp' occurrences in DSMR-readings.


Data kept/unaffected
--------------------
Historic data, such as Hour and Day Statistics are unaffected. 
These are aggregated from the Electricity & Gas Consumption data above.
This is also the only data that should matter when you want to look back to a specific day, month or year in the past.
