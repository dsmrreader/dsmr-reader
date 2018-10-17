Screenshots
===========

Below you can find screenshots of the application.


.. contents::
    :depth: 2


Dashboard
---------

The dashboard displays the latest information regarding any consumption of today and the current month so far.

.. image:: static/screenshots/frontend/dashboard.png
    :target: static/screenshots/frontend/dashboard.png
    :alt: Dashboard
    
    
Archive
-------

The archive allows you to go back to any moment tracked. The data can be plotted either on day, month or year level.

.. image:: static/screenshots/frontend/archive.png
    :target: static/screenshots/frontend/archive.png
    :alt: Archive


Compare
-------
This page allows you to compare two days, months or years tracked before. 

.. image:: static/screenshots/frontend/compare.png
    :target: static/screenshots/frontend/compare.png
    :alt: Compare


Trends
------

Trends are an average summary of your daily consumption and habits.

.. image:: static/screenshots/frontend/trends.png
    :target: static/screenshots/frontend/trends.png
    :alt: Trends


Statistics
----------

The statistics page will display the current state of your meter and the energy prices currently apply (if any).

.. image:: static/screenshots/frontend/statistics.png
    :target: static/screenshots/frontend/statistics.png
    :alt: Statistics


Energy contracts
----------------

Summary of all your contracts and the amount of energy consumed/generated. 

.. image:: static/screenshots/frontend/energy-contracts.png
    :target: static/screenshots/frontend/energy-contracts.png
    :alt: Energy contracts


Status
------

The status page shows the 'health' of the application and any data tracked.
If there are any problems regarding data handling, they should be highlighted here.

.. image:: static/screenshots/frontend/status.png
    :target: static/screenshots/frontend/status.png
    :alt: Status


Export
------
Want to export day totals or hourly data to Excel? This page allows you to export the data in .CSV format.

.. image:: static/screenshots/frontend/export.png
    :target: static/screenshots/frontend/export.png
    :alt: Export


Settings: Overview
------------------
The application has quite some features and most of them can be configured.

.. image:: static/screenshots/admin/overview.png
    :target: static/screenshots/admin/overview.png
    :alt: Configuration


Settings: API
-------------
Configure the API if you need it to supply telegrams or simply read data from DSMR-reader.

.. image:: static/screenshots/admin/apisettings.png
    :target: static/screenshots/admin/apisettings.png
    :alt: API


Settings: Backup & Dropbox
--------------------------
By default the application backs up your data locally.

.. image:: static/screenshots/admin/backupsettings.png
    :target: static/screenshots/admin/backupsettings.png
    :alt: Backup

You can use your Dropbox-account to make sure your backups are safely stored in your account. 

.. image:: static/screenshots/admin/dropboxsettings.png
    :target: static/screenshots/admin/dropboxsettings.png
    :alt: Dropbox


Settings: Datalogger & retention
--------------------------------
Configure the builtin datalogger.

.. image:: static/screenshots/admin/dataloggersettings.png
    :target: static/screenshots/admin/dataloggersettings.png
    :alt: Datalogger

All source data read is stored indefinitely, but you can apply retention, only keeping the source data for a certain amount of time.
Day statistics will never be deleted.

.. image:: static/screenshots/admin/retentionsettings.png
    :target: static/screenshots/admin/retentionsettings.png
    :alt: Datalogger


Settings: Interface
-------------------
You can change most colors used in graphs to your personal flavor. 

.. image:: static/screenshots/admin/frontendsettings.png
    :target: static/screenshots/admin/frontendsettings.png
    :alt: Interface


Settings: MinderGas.nl
----------------------
Link your MinderGas.nl-account to have DSMR-reader upload your gas meter position daily.

.. image:: static/screenshots/admin/mindergassettings.png
    :target: static/screenshots/admin/mindergassettings.png
    :alt: MinderGas


Settings: MQTT
--------------
There is support for MQTT messaging with a lot of options.

.. image:: static/screenshots/admin/mqttbrokersettings.png
    :target: static/screenshots/admin/mqttbrokersettings.png
    :alt: MQTT Broker

Get the day totals as JSON.

.. image:: static/screenshots/admin/jsondaytotalsmqttsettings.png
    :target: static/screenshots/admin/jsondaytotalsmqttsettings.png
    :alt: MQTT JSON day Totals

Or splitted per topic.

.. image:: static/screenshots/admin/splittopicdaytotalsmqttsettings.png
    :target: static/screenshots/admin/splittopicdaytotalsmqttsettings.png
    :alt: MQTT Split Topic Day Totals

Statistics of your meter.

.. image:: static/screenshots/admin/splittopicmeterstatisticsmqttsettings.png
    :target: static/screenshots/admin/splittopicmeterstatisticsmqttsettings.png
    :alt: MQTT Split Topic Meter Statistics

Telegram as JSON.

.. image:: static/screenshots/admin/jsontelegrammqttsettings.png
    :target: static/screenshots/admin/jsontelegrammqttsettings.png
    :alt: MQTT JSON Telegram

Or in raw format.

.. image:: static/screenshots/admin/rawtelegrammqttsettings.png
    :target: static/screenshots/admin/rawtelegrammqttsettings.png
    :alt: MQTT Raw Telegram

Or splitted per topic.

.. image:: static/screenshots/admin/splittopictelegrammqttsettings.png
    :target: static/screenshots/admin/splittopictelegrammqttsettings.png
    :alt: MQTT Split Topic Telegram


Settings: Notifications
-----------------------

Notifications on your phone using Prowl or Pushover. 

.. image:: static/screenshots/admin/notificationsetting.png
    :target: static/screenshots/admin/notificationsetting.png
    :alt: Notifications


Settings: PVOutput
------------------

Link your PVOutput account to upload your electricity returned.

.. image:: static/screenshots/admin/pvoutputapisettings.png
    :target: static/screenshots/admin/pvoutputapisettings.png
    :alt: PVOutput API


.. image:: static/screenshots/admin/pvoutputaddstatussettings.png
    :target: static/screenshots/admin/pvoutputaddstatussettings.png
    :alt: PVOutput Add Status


Settings: Consumption
---------------------

.. image:: static/screenshots/admin/consumptionsettings.png
    :target: static/screenshots/admin/consumptionsettings.png
    :alt: Consumption


Settings: Temperatures
----------------------

Keep track of the temperatures outside using the Buienradar API.

.. image:: static/screenshots/admin/weathersettings.png
    :target: static/screenshots/admin/weathersettings.png
    :alt: Temperatures


