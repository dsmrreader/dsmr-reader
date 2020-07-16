MQTT
====


The ``dsmr_mqtt`` process
~~~~~~~~~~~~~~~~~~~~~~~~~

Since DSMR-reader ``v4.x``, you no longer need to manually configure ``dsmr_mqtt``. It has been merged with ``dsmr_backend``.

It should be already configured while installing or upgrading DSMR-reader and listed running if you execute ``sudo supervisorctl status``.
Make sure that ``dsmr_backend`` is running.


MQTT caching
~~~~~~~~~~~~

MQTT messages are:

* Sent with the ``retain`` flag, asking the broker to cache the latest value sent to each topic.
* Cached for an hour, to reduce the number of duplicate messages sent.
* Discarded when there is already another unsent message queued with the exact same topic and contents.

This prevents duplicate messages and removes a significant overhead.