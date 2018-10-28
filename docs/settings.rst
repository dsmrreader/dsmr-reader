Other settings
==============

Some project settings can be changed (or overridden) in the ``dsmrreader/settings.py`` file. 
Removing any of these settings from your file will force using the default value.

Make sure to reload the application afterwards to persist the changes you've made by executing ``./post-deploy.sh`` or restarting the Supervisor processes.

.. contents::


``DSMRREADER_BACKEND_SLEEP``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The number of seconds the application will sleep after completing a backend run. Prevents hammering on your hardware. 

Defaults to ``DSMRREADER_BACKEND_SLEEP = 1``.


``DSMRREADER_DATALOGGER_SLEEP``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The number of seconds the application will sleep after reading data from the datalogger (API excluded). Prevents hammering on your hardware. 

Defaults to ``DSMRREADER_DATALOGGER_SLEEP = 0.5``.


``DSMRREADER_MQTT_SLEEP``
~~~~~~~~~~~~~~~~~~~~~~~~~
The number of seconds the application will sleep after reading and publishing the outgoing MQTT message queue. Prevents hammering on your hardware. 

Defaults to ``DSMRREADER_MQTT_SLEEP = 1``.


``DSMRREADER_LOG_TELEGRAMS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Whether telegrams are logged, in base64 format. Only required for debugging.

Defaults to ``DSMRREADER_LOG_TELEGRAMS = False``.


``DSMRREADER_RECONNECT_DATABASE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Whether the backend process (and datalogger) reconnects to the DB after each run. Prevents some hanging connections in some situations.

Defaults to ``DSMRREADER_RECONNECT_DATABASE = True``.


``DSMRREADER_STATUS_READING_OFFSET_MINUTES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Maximum interval in minutes allowed since the latest reading, before ringing any alarms.

Defaults to ``DSMRREADER_STATUS_READING_OFFSET_MINUTES = 60``.


``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Number of queued MQTT messages the application will retain. Any excess will be purged.

Defaults to ``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE = 100``.


``DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The maximum number of hours that will be cleaned up during one retention run. 
Raise this value if you have a lot of readings to clean up and it takes too long. 

Defaults to ``DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN = 24``.


``DSMRREADER_RETENTION_UNTIL_THIS_HOUR``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sets the maximum hour of the day that retention will run. 
Retention always starts after midnight, when enabled.
I.e.: changing it to ``8`` will prevent new retention runs after 8 A.M.

Defaults to ``DSMRREADER_RETENTION_UNTIL_THIS_HOUR = 6``.


``DSMRREADER_PLUGINS``
~~~~~~~~~~~~~~~~~~~~~~
:doc:`More information about this feature can be found here<plugins>`.

Defaults to ``DSMRREADER_PLUGINS = []``.


``DSMRREADER_DISABLED_CAPABILITIES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Whether to override (disable) capabilities. Only use if you want to disable a capability that your smart meter keeps reporting.
For example you've switched from using gas to an alternative energy source. Or your smart meter contains electricity returned data, but you do not own any solar panels.

Defaults to ``DSMRREADER_DISABLED_CAPABILITIES = []``.

Example usage ``DSMRREADER_DISABLED_CAPABILITIES = ['gas', 'electricity_returned']``.
