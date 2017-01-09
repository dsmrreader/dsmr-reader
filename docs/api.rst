API
===
The application has a simple, one-command API for remote dataloggers. It allows you to run the datalogger and application separately.


.. contents::


Configuration
-------------

Enable API
^^^^^^^^^^

The API is disabled by default in the application. You may enable it in your configuration or admin settings.

Example
~~~~~~~
.. image:: _static/screenshots/admin_api_settings.png
    :target: _static/screenshots/admin_api_settings.png
    :alt: API admin settings

Authentication
^^^^^^^^^^^^^^
Besides allowing the API to listen for requests, you will also need use the generated API Auth Key. 
It can be found on the same page as in the screenshot above. The configuration page will also display it, but only partly.
Feel free to alter the API Auth Key when required. The application initially generates one randomly for you. 

You should pass it in the header of every API call. The header should be defined as ``X-AUTHKEY``. See below for an example. 

Examples
~~~~~~~~

Using ``cURL``::

   curl http://YOUR-DSMR-URL/api/v1/datalogger/dsmrreading \
        -d 'telegram=xxxxx' \
        -H 'X-AUTHKEY: YOUR-DSMR-API-AUTHKEY'
        
Using ``requests``::

   requests.post(
        'http://YOUR-DSMR-URL/api/v1/datalogger/dsmrreading',
        headers={'X-AUTHKEY': 'YOUR-DSMR-API-AUTHKEY'},
        data={'telegram': 'xxxxx'},
    )


API calls
---------

POST ``/api/v1`` ``/datalogger/dsmrreading``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
~~~~~~~~~~~
This allows you to insert a raw telegram, read from your meter remotely, into the application as if it was read locally using the serial cable.

Parameters
~~~~~~~~~~
- Method: ``POST``
- Data: ``telegram`` (as raw string containing all linefeeds ``\n``, and carriage returns ``\r``, as well!)
- Status code returned: ``HTTP 200`` on success, any other on failure.

Example
~~~~~~~

(using the ``requests`` library available on PIP)::

    import requests  # Tested with requests==2.9.1
    
    # Fake buffer.
    telegram_string = ''.join([
        "/KFM5KAIFA-METER\r\n",
        "\r\n",
        "1-3:0.2.8(42)\r\n",
        "0-0:1.0.0(160303164347W)\r\n",
        "0-0:96.1.1(*******************************)\r\n",
        "1-0:1.8.1(001073.079*kWh)\r\n",
        "1-0:1.8.2(001263.199*kWh)\r\n",
        "1-0:2.8.1(000000.000*kWh)\r\n",
        "1-0:2.8.2(000000.000*kWh)\r\n",
        "0-0:96.14.0(0002)\r\n",
        "1-0:1.7.0(00.143*kW)\r\n",
        "1-0:2.7.0(00.000*kW)\r\n",
        "0-0:96.7.21(00006)\r\n",
        "0-0:96.7.9(00003)\r\n",
        "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483647*s)\r\n",
        "1-0:32.32.0(00000)\r\n",
        "1-0:32.36.0(00000)\r\n",
        "0-0:96.13.1()\r\n",
        "0-0:96.13.0()\r\n",
        "1-0:31.7.0(000*A)\r\n",
        "1-0:21.7.0(00.143*kW)\r\n",
        "1-0:22.7.0(00.000*kW)\r\n",
        "!74B0\n",
    ])
    
    # Register telegram by simply sending it to the application with a POST request.
    response = requests.post(
        'http://YOUR-DSMR-URL/api/v1/datalogger/dsmrreading',
        headers={'X-AUTHKEY': 'YOUR-DSMR-API-AUTHKEY'},
        data={'telegram': telegram_string},
    )
       
    # You will receive a status 200 when successful.
    if response.status_code != 200:
        # Or you will find the error (hint) in the reponse body on failure.
        print('Error: {}'.format(response.text))


Script
------
Below is a more detailed script you can use to run via Supervisor. It will send telegrams to one or multiple instances of DSMR-reader.


.. note::

    You will still require the ``dsmr`` user and VirtualEnv, :doc:`as discussed in the install guide<installation>` in **chapters 3 and 6**!

**VirtualEnv**::

    sudo su - dsmr
    pip install pyserial==3.2.1
    pip install requests==2.12.4


.. note::

    The serial connection in this example is based on ``DSMR v4``.
    
.. warning::

    Don't forget to insert your own configuration below in ``API_SERVERS``.

Client file in ``/home/dsmr/dsmr_datalogger_api_client.py``::

    from time import sleep

    from serial.serialutil import SerialException
    import requests
    import serial
    
    
    API_SERVERS = (
        ('http://HOST-OR-IP-ONE/api/v1/datalogger/dsmrreading', 'APIKEY-BLABLABLA-ABCDEFGHI'),
    ###    ('http://HOST-OR-IP-TWO/api/v1/datalogger/dsmrreading', 'APIKEY-BLABLABLA-JKLMNOPQR'),
    )
    
    
    def main():
        print ('Starting...')
    
        while True:
            telegram = read_telegram()
            print('Read telegram', telegram)
    
            for current_server in API_SERVERS:
                api_url, api_key = current_server
                send_telegram(telegram, api_url, api_key)
                print('Sent telegram to:', api_url)
    
            sleep(1)
    
    
    def read_telegram():
        """ Reads the serial port until we can create a reading point. """
        serial_handle = serial.Serial()
        serial_handle.port = '/dev/ttyUSB0'
        serial_handle.baudrate = 115200
        serial_handle.bytesize = serial.EIGHTBITS
        serial_handle.parity = serial.PARITY_NONE
        serial_handle.stopbits = serial.STOPBITS_ONE
        serial_handle.xonxoff = 1
        serial_handle.rtscts = 0
        serial_handle.timeout = 20
    
        # This might fail, but nothing we can do so just let it crash.
        serial_handle.open()
    
        telegram_start_seen = False
        telegram = ''
    
        # Just keep fetching data until we got what we were looking for.
        while True:
            try:
                data = serial_handle.readline()
            except SerialException as error:
                # Something else and unexpected failed.
                print('Serial connection failed:', error)
                return
    
            try:
                # Make sure weird characters are converted properly.
                data = str(data, 'utf-8')
            except TypeError:
                pass
    
            # This guarantees we will only parse complete telegrams. (issue #74)
            if data.startswith('/'):
                telegram_start_seen = True
    
            # Delay any logging until we've seen the start of a telegram.
            if telegram_start_seen:
                telegram += data
    
            # Telegrams ends with '!' AND we saw the start. We should have a complete telegram now.
            if data.startswith('!') and telegram_start_seen:
                serial_handle.close()
                return telegram
    
    
    def send_telegram(telegram, api_url, api_key):
        # Register telegram by simply sending it to the application with a POST request.
        response = requests.post(
            api_url,
            headers={'X-AUTHKEY': api_key},
            data={'telegram': telegram},
        )
    
        # You will receive a status 200 when successful.
        if response.status_code != 200:
            # Or you will find the error (hint) in the response body on failure.
            print('[!] Error: {}'.format(response.text))
    
    
    if __name__ == '__main__':
        main()


Supervisor config in ``/etc/supervisor/conf.d/dsmr-client.conf``::

    [program:dsmr_client_datalogger]
    command=/usr/bin/nice -n 5 /home/dsmr/.virtualenvs/dsmrclient/bin/python3 -u /home/dsmr/dsmr_datalogger_api_client.py
    pidfile=/var/tmp/dsmrreader--%(program_name)s.pid
    user=dsmr
    group=dsmr
    autostart=true
    autorestart=true
    startsecs=1
    startretries=100
    stopwaitsecs=20
    stdout_logfile=/var/log/supervisor/%(program_name)s.log
    stdout_logfile_maxbytes=10MB
    stdout_logfile_backups=3


**Supervisor**::

    sudo supervisorctl reread
    sudo supervisorctl update 
