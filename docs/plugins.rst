Plugins/hooks (Do It Yourself)
==============================
The application allows you to create and add plugins, hooking on certain events triggered.


.. contents::

Configuration
~~~~~~~~~~~~~

You can create plugins in their own file in ``dsmr_plugins/modules/plugin_name.py``, 
where ``plugin_name`` is the name of your plugin. 

Please make sure the ``plugin_name``,

* is lowercase (``plugin_name`` and **not** ``PLUGIN_NAME``),
* does not contains spaces or dashes, just use underscores and do not start the name with a digit.


Add the **dotted** path to the end of your ``dsmrreader/settings.py`` file::

    DSMRREADER_PLUGINS = [
        'dsmr_plugins.modules.plugin_name1',
        'dsmr_plugins.modules.plugin_name2',
    ]

Your plugin file is imported once, so you should make sure to hook any events you want.

And finally, make sure to **reload the application** by deploying it again. You can do that by simply executing the ``post-deploy.sh`` script in the root of the project.


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


``django.db.models.signals.post_save``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Called by Django after saving new records to the database. Can be bound to the ``DayStatistics`` model for example, to process daily statistics elsewhere.


Other
^^^^^
More signals may be available for use, please be careful when binding Django save-signals as it may impact performance.
:doc:`If you need any help or information, please seek contact via Github<contributing>`.


Example #1: Upload data to second PVOutput account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is an example of issue `#407 <https://github.com/dennissiemensma/dsmr-reader/issues/407>`_, requesting the feature to upload data to a second PVOuput account.


Settings file ``dsmrreader/settings.py`` (addition)::

    DSMRREADER_PLUGINS = [
        'dsmr_plugins.modules.pvoutput',
    ]


Plugin file ``dsmr_plugins/modules/pvoutput.py`` (new file)::

    import requests
    
    from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings
    from dsmr_pvoutput.signals import pvoutput_upload
    
    def handle_pvoutput_upload(sender, **kwargs):
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
    
    
    pvoutput_upload.connect(receiver=handle_pvoutput_upload)


Note that the ``XXXXX`` and ``YYYYY`` variables should be replace by your second set of PVOutput API credentials.


Example #2: Forwarding raw telegram data to another serial port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is an example of issue `#557 <https://github.com/dennissiemensma/dsmr-reader/issues/557>`_, allowing raw DSMR telegrams to be forwarded to another serial port.

Settings file ``dsmrreader/settings.py`` (addition)::

    DSMRREADER_PLUGINS = [
        'dsmr_plugins.modules.forward_telegram_to_serial',
    ]


Plugin file ``dsmr_plugins/modules/forward_telegram_to_serial.py`` (new file)::

    import serial
    
    from dsmr_datalogger.signals import raw_telegram
    import dsmr_datalogger.services
    
    
    def handle_forward_telegram_to_serial(sender, **kwargs):
        DEST_PORT = '/dev/ttyUSBvA'
        connection_parameters = dsmr_datalogger.services.get_dsmr_connection_parameters()
    
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
    
    
    raw_telegram.connect(receiver=handle_forward_telegram_to_serial)


Note that the ``/dev/ttyUSBvA`` variable should be changed to the serial port used in your own situation.


Example #3: Forwarding raw telegram data to another instance by API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This can be quite handy if you run multiple instances of DSMR-reader (i.e.: RaspberryPI + somewhere in cloud).

Settings file ``dsmrreader/settings.py`` (addition)::

    DSMRREADER_PLUGINS = [
        'dsmr_plugins.modules.forward_telegram_to_api',
    ]


Plugin file ``dsmr_plugins/modules/forward_telegram_to_api.py`` (new file)::

    import requests
    import logging
    
    from dsmr_datalogger.signals import raw_telegram
    
    
    def handle_forward_telegram_to_api(sender, **kwargs):
        API_HOST = 'https://YOUR-DSMR-HOST'  # Note: Check whether you use HTTP or SSL (HTTPS).
        API_KEY = 'YOUR-API-KEY'
        TIMEOUT = 5  # A low timeout prevents the application from hanging too long if the server is unavailable.
    
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
    
        # You will receive a status 201 when successful.
        if response.status_code != 201:
            # Or you will find the error (hint) in the reponse body on failure.
            logging.error('Server Error forwarding telegram: {}'.format(response.text))
    
    
    raw_telegram.connect(receiver=handle_forward_telegram_to_api)


Note that the ``API_HOST``, ``API_KEY`` and ``TIMEOUT`` variables should be changed to your own preferences. 


Example #4: Forwarding DSMR readings in JSON format to some API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use this to send DSMR readings in JSON format to some (arbitrary) API.

Settings file ``dsmrreader/settings.py`` (addition)::

    DSMRREADER_PLUGINS = [
        'dsmr_plugins.modules.forward_json_dsmrreading_to_api',
    ]


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
