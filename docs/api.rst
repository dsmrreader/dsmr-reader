API
===
The application has a simple, one-command API for remote dataloggers.


Configuration
-------------

Enable API
^^^^^^^^^^

By default the API is disabled in the application. You may enable it in your configuration or admin settings.

.. image:: _static/screenshots/admin_api_settings.png
    :target: _static/screenshots/admin_api_settings.png
    :alt: API admin settings

Authentication
^^^^^^^^^^^^^^
Besides allowing the API to listen for requests, you will also need use the generated API Auth Key. 
It can be found on the same page as in the screenshot above. The configuration page will also display it, but only partly.
Feel free to alter the API Auth Key when required. The application randomly generates one initially for you. 

You should pass it in the header of every API call. The header should be defined as ``X-AUTHKEY``. See below for an example. 

Examples
^^^^^^^^

Using ``cURL``::

   curl http://YOUR-DSMR-URL/api/v1/endpointX \
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
This allows you to insert a raw telegram, read from your meter remotely, into the application as if it was read locally using the serial cable.

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
    