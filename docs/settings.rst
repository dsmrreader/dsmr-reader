Custom settings
===============

.. warning::

    Since DSMR-reader ``v2.14.0`` these settings were relocated to the webinterface or removed entirely::

        (relocated)   DSMRREADER_BACKEND_SLEEP
        (relocated)   DSMRREADER_DATALOGGER_SLEEP
        (relocated)   DSMRREADER_MQTT_SLEEP
        (relocated)   DSMRREADER_LOG_TELEGRAMS
        (relocated)   DSMRREADER_DISABLED_CAPABILITIES

        (removed)     DSMRREADER_RECONNECT_DATABASE
        (removed)     DSMRREADER_STATUS_READING_OFFSET_MINUTES
        (removed)     DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE
        (removed)     DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN

Some project settings can be changed (or overridden) in the ``dsmrreader/settings.py`` file. 
Removing any of these settings from your file will force using the default value.

Make sure to reload the application afterwards to persist the changes you've made by executing ``./post-deploy.sh`` or restarting the Supervisor processes.

.. contents::


``DSMRREADER_BACKEND_SLEEP``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **moved to the webinterface**.

The number of seconds the application will sleep after completing a backend run. Prevents hammering on your hardware. 

Defaults to ``DSMRREADER_BACKEND_SLEEP = 1``.


``DSMRREADER_DATALOGGER_SLEEP``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **moved to the webinterface**.

The number of seconds the application will sleep after reading data from the datalogger (API excluded). Prevents hammering on your hardware. 

Defaults to ``DSMRREADER_DATALOGGER_SLEEP = 0.5``.


``DSMRREADER_MQTT_SLEEP``
~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **moved to the webinterface**.

The number of seconds the application will sleep after reading and publishing the outgoing MQTT message queue. Prevents hammering on your hardware. 

Defaults to ``DSMRREADER_MQTT_SLEEP = 1``.


``DSMRREADER_LOG_TELEGRAMS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **moved to the webinterface**.

Whether telegrams are logged, in base64 format. Only required for debugging.

Defaults to ``DSMRREADER_LOG_TELEGRAMS = False``.


``DSMRREADER_RECONNECT_DATABASE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **removed**.

Whether the backend process (and datalogger) reconnects to the DB after each run. Prevents some hanging connections in some situations.

Defaults to ``DSMRREADER_RECONNECT_DATABASE = True``.


``DSMRREADER_STATUS_READING_OFFSET_MINUTES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **removed**.

Maximum interval in minutes allowed since the latest reading, before ringing any alarms.

Defaults to ``DSMRREADER_STATUS_READING_OFFSET_MINUTES = 60``.


``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **removed**.

Number of queued MQTT messages the application will retain. Any excess will be purged.

Defaults to ``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE = 200``.


``DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **removed**.

The maximum number of hours that will be cleaned up during one retention run. 
Raise this value if you have a lot of readings to clean up and it takes too long. 

Defaults to ``DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN = 24``.


``DSMRREADER_DISABLED_CAPABILITIES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Since DSMR-reader ``v2.14.0`` this setting was **moved to the webinterface**.

Whether to override (disable) capabilities. Only use if you want to disable a capability that your smart meter keeps reporting.
For example you've switched from using gas to an alternative energy source. Or your smart meter contains electricity returned data, but you do not own any solar panels.

Defaults to ``DSMRREADER_DISABLED_CAPABILITIES = []``.

Example usage ``DSMRREADER_DISABLED_CAPABILITIES = ['gas', 'electricity_returned']``.
