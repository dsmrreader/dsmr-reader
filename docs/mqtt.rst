MQTT
====

The application supports sending MQTT messages to your broker.

.. contents::


Configuration
-------------
Support for MQTT is disabled by default in the application. You may enable it in your configuration or admin settings.


Events
------
The following events can trigger MQTT messages when enabled:

Raw telegrams
^^^^^^^^^^^^^
Each time a telegram is read via the v1 API or datalogger. You can have the entire telegram string passed on to your MQTT broker.

Reading creation
^^^^^^^^^^^^^^^^
Each time a new reading is parsed, either created by the datalogger or v1/v2 API. 
You can have each parsed reading passed on to your broker either in JSON format or on a per-field per-topic basis.
