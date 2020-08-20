Introduction
============

Project goals
-------------
- Provide a tool to easily extract and store data transferred by the DSMR protocol of your smart meter.
- Allowing to export your data to other systems or third parties. It's your data, you decide.


Features
--------
DSMR-reader has the following features:

- Read telegram data from serial port
- Read telegram data from network socket
- Receive telegram data through its (REST) API
- Process, store and plot telegram data extensively
- Daily cost indication using your energy prices
- Push notifications through Pushover / Prowl
- Automated export to your MinderGas.nl account
- Automated export to your PVOutput.org account
- Automated export to an MQTT broker
- Automated export to an InfluxDB
- Automated backup to Dropbox
- Automated backup through email
- And many others...


Screenshots / tour
------------------
:doc:`For more screenshots see this page<tour>`.


Languages
---------
The entire application and its code is written and documented in English.
The interface is translated into Dutch and will be enabled automatically, depending on your browser's language preference.

Support for:

- English
- Dutch


Storage issues
--------------
.. warning::

    :doc:`Please read this page as well before using DSMR-reader<data_integrity>`.
