Backend settings
================

The application has several settings available, which you can edit in the Configuration page.
The default settings should work fine, although it's recommended to enable syncing backups using Dropbox. 

.. contents::


Database/Django settings
------------------------
``dsmrreader/settings.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~
In case you want to alter the database settings, or any other Django settings, please modify (or add) them to the ``dsmrreader/settings.py`` file.

Make sure to reload the application afterwards to persist the changes you've made, by executing ``./reload.sh`` or restarting the Supervisor processes.


API configuration
-----------------

The application does have an API, but it's disabled by default.
You can enable it by activating the "Allow API calls" option.

``Allow API calls``
~~~~~~~~~~~~~~~~~~~
Whether the API is enabled.

``Auth Key``
~~~~~~~~~~~~
The auth key used for authentication.



Backup configuration
--------------------
The application creates a daily database backup by default. 
You choose whether you want to have it compressed or in raw SQL form.
The timestamp of the backup can be altered as well.

``Backup daily``
~~~~~~~~~~~~~~~~
Whether to created backups at all.

``Compress``
~~~~~~~~~~~~
Enable this to have the backups compressed in gzip format.
Highly recommended as it will make backups up to 10 times smaller!  

``Backup timestamp``
~~~~~~~~~~~~~~~~~~~~
Timestamp of the daily backup.



Dropbox configuration
---------------------
There is a Dropbox integration available to safely transfer each daily backup into your Dropbox account.
:doc:`More information about this feature can be found in the FAQ<faq>`.

``Dropbox access token``
~~~~~~~~~~~~~~~~~~~~~~~~
Enter your Dropbox access token here. Leave blank or clear to disable Dropbox integration.



Consumption configuration
-------------------------
The consumption settings determine how the application should handle the separate readings.
The default behaviour is to group all readings each minute. This can be disabled.

``Compactor grouping type``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The density of the readings, visible in the application as consumption.



Energy supplier prices
----------------------
You can enter all your energy contract prices here. 
The application will use them (when available) to calculate the consumption of each day.
:doc:`See the FAQ on how to retroactivily adjust prices (if needed)<faq>`.



Datalogger configuration
------------------------
This configuration applies to how to read your smart meter.

``Poll P1 port``
~~~~~~~~~~~~~~~~
Do not disable this. Will be removed next release.

``Track electricity phases``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Whether you want to track phases. 
:doc:`More information about this feature can be found in the FAQ<faq>`.

``Verify telegram CRC``
~~~~~~~~~~~~~~~~~~~~~~~
Whether the application should verify the incoming data. Only available for DSMR 4+.

``DSMR version``
~~~~~~~~~~~~~~~~
The DSMR version your smart meter has. Used to determine how the serial connection should work.

``COM-port``
~~~~~~~~~~~~
The COM port your cable can be read from.



Retention configuration
-----------------------
Data retention applied to the readings stored in the application.

``Data retention``
~~~~~~~~~~~~~~~~~~
Whether to delete old readings, and which period of time should have elapsed, before deleting them.



Frontend configuration
----------------------
This applies to the visualisation in the application.

``Merge electricity tariffs``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Whether to merge the high and low tariffs. 
:doc:`More information about this feature can be found in the FAQ<faq>`.

``**** color``
~~~~~~~~~~~~~~
Multiple colors can be set here for the graphs.



MinderGas.nl configuration
--------------------------
Optional connection with your account at MinderGas.nl. 
:doc:`More information about this feature can be found in the FAQ<faq>`.


``Export data to MinderGas``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Whether to enable the connecting with MinderGas.

``MinderGas authentication token``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
API token for your MinderGas.nl account.



Notes
-----
You can leave personal notes for yourself here. 
Such as when you were on holiday or experimented with the heater settings. 



Notification configuration
--------------------------
Allows sending daily notifications to your phone. 
:doc:`More information about this feature can be found in the FAQ<faq>`.

``Send notification``
~~~~~~~~~~~~~~~~~~~~~
Whether to enable this feature.

``Notification service``
~~~~~~~~~~~~~~~~~~~~~~~~
The notification service you are using.

``Notification service API key``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
API token for your account of the notification service.


Weather configuration
---------------------
There is support for tracking outside temperatures for a fixed number of weather stations. 
:doc:`More information about this feature can be found in the FAQ<faq>`.

``Track weather``
~~~~~~~~~~~~~~~~~
Whether to enable this feature.

``Buienradar weather station``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The fixed weather station you wish to use.

