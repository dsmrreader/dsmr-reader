Plugins
=======

The application allows you to create and add plugins, hooking on certain events triggered.


.. contents::

Configuration
~~~~~~~~~~~~~

You can create plugins in their own file in ``dsmr_plugins/modules/plugin_name.py``, 
where ``plugin_name`` is the name of your plugin. 

Please make sure the ``plugin_name``,

* is lowercase (``plugin_name`` and **not** ``PLUGIN_NAME``),
* does not contains spaces or dashes, only use underscores and do not start the name with a digit.

.. seealso::

    Add the **dotted** path as ``DSMRREADER_PLUGINS`` env var. For more information :doc:`see DSMRREADER_PLUGINS in Env Settings<env_settings>`.

Your plugin file is imported once, so you should make sure to hook any events you want.

And finally, make sure to **restart the application** to reflect the changes.
Do so by executing the following as **root user or sudoer**::

    sudo supervisorctl restart all


Events / Signals
----------------
These are either dispatched by the Django framework or the application at some point.

``dsmr_backend.signals.backend_called``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Called by each iteration of the backend. Please use with caution, as it may block all backend operations when used improperly.


``dsmr_pvoutput.signals.pvoutput_upload``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Called by dsmr_pvoutput just before uploading data to PVOutput. The ``data`` kwarg contains the data to be sent.


``dsmr_datalogger.signals.raw_telegram``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Called by dsmr_datalogger when receiving or reading a telegram string. The ``data`` kwarg contains the raw telegram string.


``dsmr_notification.signals.notification_sent``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Called by dsmr_notification just after dispatching a notification. The ``title`` kwarg contains the notification title, ``message`` contains the message body.


``django.db.models.signals.post_save``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Called by Django after saving new records to the database. Can be bound to the ``DayStatistics`` model for example, to process daily statistics elsewhere.


Other
^^^^^
More signals may be available for use, please be careful when binding Django save-signals as it may impact performance.


Examples:
~~~~~~~~~

Example #1: Upload data to second PVOutput account
--------------------------------------------------
This is an example of issue `#407 <https://github.com/dsmrreader/dsmr-reader/issues/407>`_, requesting the feature to upload data to a second PVOuput account.

.. seealso::

    :doc:`DSMRREADER_PLUGINS configuration<env_settings>`::

        DSMRREADER_PLUGINS=dsmr_plugins.modules.secondary_pvoutput_upload


Plugin file ``dsmr_plugins/modules/secondary_pvoutput_upload.py`` (new file)::

    import requests

    from django.dispatch import receiver

    from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings
    from dsmr_pvoutput.signals import pvoutput_upload


    @receiver(pvoutput_upload)
    def handle_secondary_pvoutput_upload(**kwargs):
        print(' - Uploading the same data to PVOutput using plugin: {}'.format(kwargs['data']))

        response = requests.post(
            PVOutputAddStatusSettings.API_URL,
            headers={
                'X-Pvoutput-Apikey': 'XXXXX',
                'X-Pvoutput-SystemId': 'YYYYY',
            },
            data=kwargs['data']
        )

        if response.status_code != 200:
            print(' [!] PVOutput upload failed (HTTP {}): {}'.format(response.status_code, response.text))

.. attention::

    Note that the ``XXXXX`` and ``YYYYY`` variables should be replace by your second set of PVOutput API credentials.


Example #2: Forwarding raw telegram data to another serial port
---------------------------------------------------------------
This is an example of issue `#557 <https://github.com/dsmrreader/dsmr-reader/issues/557>`_, allowing raw DSMR telegrams to be forwarded to another serial port.

.. seealso::

    :doc:`DSMRREADER_PLUGINS configuration<env_settings>`::

        DSMRREADER_PLUGINS=dsmr_plugins.modules.forward_raw_telegram_to_serial


Plugin file ``dsmr_plugins/modules/forward_raw_telegram_to_serial.py`` (new file)::

    import serial

    from django.dispatch import receiver

    from dsmr_datalogger.signals import raw_telegram
    import dsmr_datalogger.services.datalogger


    @receiver(raw_telegram)
    def handle_forward_raw_telegram_to_serial(**kwargs):
        DEST_PORT = '/dev/ttyUSBvA'
        connection_parameters = dsmr_datalogger.services.datalogger.get_dsmr_connection_parameters()

        serial_handle = serial.Serial()
        serial_handle.port = DEST_PORT
        serial_handle.baudrate = connection_parameters['baudrate']
        serial_handle.bytesize = connection_parameters['bytesize']
        serial_handle.parity = connection_parameters['parity']
        serial_handle.stopbits = serial.STOPBITS_ONE
        serial_handle.xonxoff = 1
        serial_handle.rtscts = 0
        serial_handle.timeout = 1
        serial_handle.write_timeout = 0.2

        try:
            serial_handle.open()
            bytes_sent = serial_handle.write(bytes(kwargs['data'], 'utf-8'))
        except Exception as error:
            print(error)
        else:
            print(' >>> Sent {} bytes to {}'.format(bytes_sent, DEST_PORT))

        serial_handle.close()


.. attention::

    Note that the ``/dev/ttyUSBvA`` variable should be changed to the serial port used in your own situation.


Example #3: Forwarding raw telegram data to another instance by API
-------------------------------------------------------------------
This can be quite handy if you run multiple instances of DSMR-reader (i.e.: RaspberryPI + somewhere in cloud).

.. seealso::

    :doc:`DSMRREADER_PLUGINS configuration<env_settings>`::

        DSMRREADER_PLUGINS=dsmr_plugins.modules.forward_raw_telegram_to_api


Plugin file ``dsmr_plugins/modules/forward_raw_telegram_to_api.py`` (new file)::

    import requests
    import logging

    from django.dispatch import receiver

    from dsmr_datalogger.signals import raw_telegram


    @receiver(raw_telegram)
    def handle_forward_raw_telegram_to_api(**kwargs):
        API_HOST = 'https://YOUR-DSMR-HOST'  # Note: Check whether you use HTTP or SSL (HTTPS).
        API_KEY = 'YOUR-API-KEY'
        TIMEOUT = 5  # A low timeout prevents the application from hanging, when the server is unavailable.

        try:
            # Register telegram by simply sending it to the application with a POST request.
            response = requests.post(
                '{}/api/v1/datalogger/dsmrreading'.format(API_HOST),
                headers={'X-AUTHKEY': API_KEY},
                data={'telegram': kwargs['data']},
                timeout=TIMEOUT
            )
        except Exception as error:
            return logging.error(error)

        if response.status_code != 201:
            logging.error('Server Error forwarding telegram: {}'.format(response.text))


.. attention::

    Note that the ``API_HOST``, ``API_KEY`` and ``TIMEOUT`` variables should be changed to your own preferences.


Example #4: Forwarding DSMR readings in JSON format to some API
---------------------------------------------------------------
Use this to send DSMR readings in JSON format to some (arbitrary) API.

.. seealso::

    :doc:`DSMRREADER_PLUGINS configuration<env_settings>`::

        DSMRREADER_PLUGINS=dsmr_plugins.modules.forward_json_dsmrreading_to_api


Plugin file ``dsmr_plugins/modules/forward_json_dsmrreading_to_api.py`` (new file)::

    import requests
    import json

    from django.dispatch import receiver
    from django.core import serializers
    from django.utils import timezone
    import django.db.models.signals

    from dsmr_datalogger.models.reading import DsmrReading

    @receiver(django.db.models.signals.post_save, sender=DsmrReading)
    def handle_forward_json_dsmrreading_to_api(sender, instance, created, raw, **kwargs):
        if not created or raw:
            return

        instance.timestamp = timezone.localtime(instance.timestamp)

        if instance.extra_device_timestamp:
            instance.extra_device_timestamp = timezone.localtime(instance.extra_device_timestamp)

        serialized = json.loads(serializers.serialize('json', [instance]))
        json_string = json.dumps(serialized[0]['fields'])

        try:
            requests.post(
                'https://YOUR-DSMR-HOST/api/endpoint/',
                data=json_string,
                # A low timeout prevents DSMR-reader from hanging, when the remote server is unreachable.
                timeout=5
            )
        except Exception as error:
            print('forward_json_dsmrreading_to_api:', error)


Example #5: Read telegrams using DSMRloggerWS API
-------------------------------------------------

.. seealso::

    :doc:`DSMRREADER_PLUGINS configuration<env_settings>`::

        DSMRREADER_PLUGINS=dsmr_plugins.modules.poll_dsmrloggerws_api


Plugin file ``dsmr_plugins/modules/poll_dsmrloggerws_api.py`` (new file)::

    import requests

    from django.dispatch import receiver

    from dsmr_backend.signals import backend_called
    import dsmr_datalogger.services.datalogger


    # Preverve a low timeout to prevent the entire backend process from hanging too long.
    DSMRLOGGERWS_ENDPOINT = 'http://localhost/api/v1/sm/telegram'
    DSMRLOGGERWS_TIMEOUT = 5


    @receiver(backend_called)
    def handle_backend_called(**kwargs):
        response = requests.get(DSMRLOGGERWS_ENDPOINT,
                                timeout=DSMRLOGGERWS_TIMEOUT)

        if response.status_code != 200:
            print(' [!] DSMRloggerWS plugin: Telegram endpoint failed (HTTP {}): {}'.format(
                response.status_code,
                response.text
            ))
            return

        dsmr_datalogger.services.datalogger.telegram_to_reading(data=response.text)

.. attention::

    Note that you might need to update the ``http://localhost`` value to your own situation.
