MQTT
====

.. warning::

    Only follow these step if you have enabled MQTT.


Older versions (< v1.23.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from ``v1.23.0`` DSMR-reader requires a dedicated process for processing MQTT messages (``dsmr_mqtt``).

Fresh installations automatically include the ``dsmr_mqtt`` process. Existing installations however, should add ``dsmr_mqtt`` manually. Instructions:

* Please upgrade to ``v1.23.0`` or higher first.
* Now execute the following commands as **root/sudo-user**::

    # NOTE: This will overwrite /etc/supervisor/conf.d/dsmr-reader.conf
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr-reader.conf /etc/supervisor/conf.d/


Starting MQTT
~~~~~~~~~~~~~

* Execute ``sudo supervisorctl status`` and check whether it includes ``dsmr_mqtt`` with status ``RUNNING``. If not, continue with the steps below.

* Open ``/etc/supervisor/conf.d/dsmr-reader.conf`` (sudo required) and find::

    [program:dsmr_mqtt]
    environment=PYTHONUNBUFFERED=1
    command=/usr/bin/nice -n 15 /home/dsmr/.virtualenvs/dsmrreader/bin/python3 -u /home/dsmr/dsmr-reader/manage.py dsmr_mqtt
    directory=/home/dsmr/dsmr-reader/
    user=dsmr
    group=dsmr
    ### To enable: set 'autostart=true' below.
    ### Then execute: "sudo supervisorctl reread" and "sudo supervisorctl update"
    autostart=false
    autorestart=true

* Change::

    autostart=false

* To::

    autostart=true

* Save the file.

* Apply changes::

    sudo supervisorctl reread
    sudo supervisorctl update

* Executing ``sudo supervisorctl status`` should now include ``dsmr_mqtt`` with status ``RUNNING``.