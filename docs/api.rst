API Documentation
=================
The application has an API allowing you to insert/create readings and retrieve statistics.


.. contents::


Configuration & authentication
------------------------------

Enable API
^^^^^^^^^^

The API is disabled by default in the application. You may enable it in your configuration or admin settings.

Example
~~~~~~~
.. image:: _static/screenshots/admin/apisettings.png
    :target: _static/screenshots/admin/apisettings.png
    :alt: API admin settings

Authenticating
^^^^^^^^^^^^^^
Besides allowing the API to listen for requests, you will also need send your API key with each request. 
The API key can be found on the same page as in the screenshot above.
The application generates one for you initially, but feel free to alter the API key when required.

You should pass it in the header of every API call. See below for an example.
Since ``v2.1.0``, you should not longer use ``X-AUTHKEY``.
Use ``Authorization`` with value ``Token <key>`` instead.

Examples
~~~~~~~~

Using ``cURL``::

    # Don't forget to replace 'YOUR-DSMR-URL' and 'YOUR-API-KEY' with your own values.
    curl http://YOUR-DSMR-URL/api/v1/datalogger/dsmrreading \
        -d 'telegram=xxxxx' \
        -H 'Authorization: Token YOUR-API-KEY'
   
    # Or use

    curl http://YOUR-DSMR-URL/api/v1/datalogger/dsmrreading \
        -d 'telegram=xxxxx' \
        -H 'Authorization: Token YOUR-API-KEY'
     
Using ``requests``::

    requests.post(
        'http://YOUR-DSMR-URL/api/v1/datalogger/dsmrreading',
        headers={'Authorization': 'Token YOUR-API-KEY'},
        data={'telegram': 'xxxxx'},
    )
   
    # Or use

    requests.post(
        'http://YOUR-DSMR-URL/api/v1/datalogger/dsmrreading',
        headers={'Authorization': 'Token YOUR-API-KEY'},
        data={'telegram': 'xxxxx'},
    )


[API v1] Remote datalogger
--------------------------

``POST`` - ``datalogger/dsmrreading``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This allows you to insert a raw telegram, into the application as if it was read locally using the serial cable.

.. note::

    Since ``DSMR-reader v1.6`` this call now returns ``HTTP 201`` instead of ``HTTP 200`` when successful.


URI
~~~
Full path: ``/api/v1/datalogger/dsmrreading``


Parameters
~~~~~~~~~~

- ``telegram`` (*string*) - The raw telegram string containing all linefeeds ``\n``, and carriage returns ``\r``, as well!


Response
~~~~~~~~
``HTTP 201`` on success, with empty body. Any other status code on failure.


Example
~~~~~~~

(using the ``requests`` library available on PIP)::

    import requests  # Tested with requests==2.9.1

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
        headers={'Authorization': 'Token YOUR-API-KEY'},
        data={'telegram': telegram_string},
    )

    # You will receive a status 201 when successful.
    if response.status_code != 201:
        # Or you will find the error (hint) in the reponse body on failure.
        print('Error: {}'.format(response.text))


Script
~~~~~~
You can use a script to run in Supervisor. It will send telegrams to one or multiple instances of DSMR-reader.
For detailed installation instructions, see :doc:`install guide for datalogger only<installation/datalogger>`.

----
    

[API v2] RESTful API
--------------------

.. note::

    These API calls are available since ``v1.7``.


``POST`` - ``datalogger/dsmrreading``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creates a reading from direct values, omitting the need for the telegram. 

.. note::

    **Please note**: Readings are processed simultaneously. Inserting readings **retroactively** might result in undesired results due to the data processing, which is always reading ahead.
    
    Therefor inserting historic data might require you to delete all aggregated data using::

        sudo su - postgres
        psql dsmrreader
        truncate dsmr_consumption_electricityconsumption;
        truncate dsmr_consumption_gasconsumption;
        truncate dsmr_stats_daystatistics;
        truncate dsmr_stats_hourstatistics;

        # This query can take a long time!
        update dsmr_datalogger_dsmrreading set processed = False;

    
    This will process all readings again, from the very first start, and aggregate them (and **will** take a long time depending on your reading count).
    
    Please note that the datalogger may interfere. If your stats are not correctly after regenerating, try it again while having your datalogger disabled.


URI
~~~
Full path: ``/api/v2/datalogger/dsmrreading``


Parameters
~~~~~~~~~~
**[R]** = Required field

- **[R]** ``timestamp`` (*datetime*) - Timestamp indicating when the reading was taken, according to the smart meter
- **[R]** ``electricity_currently_delivered`` (*float*) - Current electricity delivered in kW
- **[R]** ``electricity_currently_returned`` (*float*) - Current electricity returned in kW
- **[R]** ``electricity_delivered_1`` (*float*) - Meter position stating electricity delivered (low tariff) in kWh
- **[R]** ``electricity_delivered_2`` (*float*) - Meter position stating electricity delivered (normal tariff) in kWh
- **[R]** ``electricity_returned_1`` (*float*) - Meter position stating electricity returned (low tariff) in kWh
- **[R]** ``electricity_returned_2`` (*float*) - Meter position stating electricity returned (normal tariff) in kWh
- ``phase_currently_delivered_l1`` (*float*) - Current electricity used by phase L1 (in kW)
- ``phase_currently_delivered_l2`` (*float*) - Current electricity used by phase L2 (in kW)
- ``phase_currently_delivered_l3`` (*float*) - Current electricity used by phase L3 (in kW)
- ``phase_currently_returned_l1`` (*float*) - Current electricity returned by phase L1 (in kW)
- ``phase_currently_returned_l2`` (*float*) - Current electricity returned by phase L2 (in kW)
- ``phase_currently_returned_l3`` (*float*) - Current electricity returned by phase L3 (in kW)
- ``extra_device_timestamp`` (*datetime*) - Last timestamp read from the extra device connected (gas meter)
- ``extra_device_delivered`` (*float*) - Last value read from the extra device connected (gas meter)

.. note::

    **datetime format** = ``YYYY-MM-DDThh:mm[:ss][+HH:MM|-HH:MM|Z]``, i.e.: ``2017-01-01T12:00:00+01`` (CET), ``2017-04-15T12:00:00+02`` (CEST) or ``2017-04-15T100:00:00Z`` (UTC).

Response
~~~~~~~~
``HTTP 201`` on success. Body contains the reading created in JSON format. Any other status code on failure.


Example
~~~~~~~
**Data** to insert::

    electricity_currently_delivered: 1.500
    electricity_currently_returned: 0.025
    electricity_delivered_1: 2000
    electricity_delivered_2: 3000
    electricity_returned_1: 0
    electricity_returned_2: 0
    timestamp: 2017-04-15T00:00:00+02


Using **cURL** (commandline)::

    # Don't forget to replace 'YOUR-DSMR-URL' and 'YOUR-API-KEY' with your own values.
    # Please note that the plus symbol "+" has been replaced by "%2B" here, to make it work for cURL.
    curl http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading \
          -d 'timestamp=2017-04-15T00:00:00%2B02&electricity_currently_delivered=1.5&electricity_currently_returned=0.025&electricity_delivered_1=2000&electricity_delivered_2=3000&electricity_returned_1=0&electricity_returned_2=0' \
          -H 'Authorization: Token YOUR-API-KEY' | python -m json.tool


Using **requests** (Python)::

    import requests
    import json

    response = requests.post(
        'http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading',
        headers={'Authorization': 'Token YOUR-API-KEY'},
        data={
            'electricity_currently_delivered': 1.500,
            'electricity_currently_returned': 0.025,
            'electricity_delivered_1': 2000,
            'electricity_delivered_2': 3000,
            'electricity_returned_1': 0,
            'electricity_returned_2': 0,
            'timestamp': '2017-04-15T00:00:00+02',
        }
    )

    if response.status_code != 201:
        print('Error: {}'.format(response.text))
    else:
        print('Created: {}'.format(json.loads(response.text)))

          
**Result**::

    {
        "id": 4343119,
        "timestamp": "2017-04-15T00:00:00+02:00",
        "electricity_delivered_1": "2000.000",
        "electricity_returned_1": "0.000",
        "electricity_delivered_2": "3000.000",
        "electricity_returned_2": "0.000",
        "electricity_currently_delivered": "1.500",
        "electricity_currently_returned": "0.025",
        "phase_currently_delivered_l1": null,
        "phase_currently_delivered_l2": null,
        "phase_currently_delivered_l3": null,
        "phase_currently_returned_l1": null,
        "phase_currently_returned_l2": null,
        "phase_currently_returned_l3": null,
        "extra_device_timestamp": null,
        "extra_device_delivered": null
    }
    
    
----
    

``GET`` - ``datalogger/dsmrreading``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retrieves any readings stored. The readings are either constructed from incoming telegrams or were created using this API.


URI
~~~
Full path: ``/api/v2/datalogger/dsmrreading``


Parameters
~~~~~~~~~~
All parameters are optional.

- ``timestamp__gte`` (*datetime*) - Limits the result to any readings having a timestamp **higher or equal** to this parameter.
- ``timestamp__lte`` (*datetime*) - Limits the result to any readings having a timestamp **lower or equal** to this parameter.
- ``ordering`` (*string*) - Use ``-timestamp`` to sort **descending**. Omit or use ``timestamp`` to sort **ascending** (default).
- ``offset`` (*integer*) - When iterating large resultsets, the offset determines the starting point.
- ``limit`` (*integer*) - Limits the resultset size returned. Omit for maintaining the default limit (**25**).


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


.. _generic-examples-anchor:

Example 1 - Fetch all readings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This demonstrates how to fetch all readings stored, without using any of the parameters. 


Using **cURL** (commandline)::

    # Don't forget to replace 'YOUR-DSMR-URL' and 'YOUR-API-KEY' with your own values.
    curl 'http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading' \
      -H 'Authorization: Token YOUR-API-KEY' | python -m json.tool


Using **requests** (Python)::

    import requests
    import json

    response = requests.get(
        'http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading',
        headers={'Authorization': 'Token YOUR-API-KEY'},
    )

    if response.status_code != 200:
        print('Error: {}'.format(response.text))
    else:
        print('Response: {}'.format(json.loads(response.text)))


**Result**::

    # Please note that by default only 25 results are returned. The actual number of results
    # is available in the 'count' field. You can iterate these using the offset-parameter.    
    {
        "count": 4343060,
        "next": "http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading?limit=25&offset=25",
        "previous": null,
        "results": [
            {
                "id": 1,
                "timestamp": "2015-12-11T21:25:05Z",
                "electricity_delivered_1": "594.560",
                "electricity_returned_1": "0.000",
                "electricity_delivered_2": "593.006",
                "electricity_returned_2": "0.000",
                "electricity_currently_delivered": "0.183",
                "electricity_currently_returned": "0.000",
                "phase_currently_delivered_l1": null,
                "phase_currently_delivered_l2": null,
                "phase_currently_delivered_l3": null,
                "phase_currently_returned_l1": null,
                "phase_currently_returned_l2": null,
                "phase_currently_returned_l3": null,
                "extra_device_timestamp": "2015-12-11T21:00:00Z",
                "extra_device_delivered": "956.212"
            },
            ... <MORE RESULTS> ...
        ]
    }
    

Example 2 - Fetch latest reading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This demonstrates how to fetch the latest reading stored. Therefor we request all readings, sort them descending by timestamp and limit the result to only one.


Using **cURL** (commandline)::

    # Don't forget to replace 'YOUR-DSMR-URL' and 'YOUR-API-KEY' with your own values.
    curl 'http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading?ordering=-timestamp&limit=1' \
        -H 'Authorization: Token YOUR-API-KEY' | python -m json.tool


Using **requests** (Python)::

    import requests
    import json

    response = requests.get(
        'http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading?ordering=-timestamp&limit=1',
        headers={'Authorization': 'Token YOUR-API-KEY'},
    )

    if response.status_code != 200:
        print('Error: {}'.format(response.text))
    else:
        print('Response: {}'.format(json.loads(response.text)))


**Result**::

    # This should present you the latest reading (determined by the timestamp field)
    {
        "count": 4343060,
        "next": "http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading?limit=1&offset=1&ordering=-timestamp",
        "previous": null,
        "results": [
            {
                "id": 4343116,
                "timestamp": "2017-04-29T03:59:25Z",
                "electricity_delivered_1": "1871.589",
                "electricity_returned_1": "0.000",
                "electricity_delivered_2": "1756.704",
                "electricity_returned_2": "0.000",
                "electricity_currently_delivered": "0.078",
                "electricity_currently_returned": "0.000",
                "phase_currently_delivered_l1": "0.024",
                "phase_currently_delivered_l2": "0.054",
                "phase_currently_delivered_l3": "0.000",
                "phase_currently_returned_l1": "0.000",
                "phase_currently_returned_l2": "0.000",
                "phase_currently_returned_l3": "0.000",
                "extra_device_timestamp": "2017-04-29T03:00:00Z",
                "extra_device_delivered": "1971.929"
            }
        ]
    }


Example 3 - Fetch readings by month
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This demonstrates how to fetch all readings within a month. We limit the search by specifying the month start and end.


Using **cURL** (commandline)::

    # Don't forget to replace 'YOUR-DSMR-URL' and 'YOUR-API-KEY' with your own values.
    # Note that the whitespace in the timestamps has been converted to '%20' for cURL.
    curl 'http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading?timestamp__gte=2017-02-01%2000:00:00&timestamp__lte=2017-03-01%2000:00:00' \
        -H 'Authorization: Token YOUR-API-KEY' | python -m json.tool


Using **requests** (Python)::

    import requests
    import json

    response = requests.get(
        'http://YOUR-DSMR-URL/api/v2/statistics/day?timestamp__gte=2017-02-01 00:00:00&timestamp__lte=2017-03-01 00:00:00',
        headers={'Authorization': 'Token YOUR-API-KEY'},
    )

    if response.status_code != 200:
        print('Error: {}'.format(response.text))
    else:
        print('Response: {}'.format(json.loads(response.text)))
        
        
**Result**::

    # This should present you a set of all readings in the month selected.
    {
        "count": 240968,
        "next": "http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading?limit=25&offset=25&timestamp__gte=2017-02-01+00%3A00%3A00&timestamp__lte=2017-03-01+00%3A00%3A00",
        "previous": null,
        "results": [
            {
                "id": 3593621,
                "timestamp": "2017-01-31T23:00:03Z",
                "electricity_delivered_1": "1596.234",
                "electricity_returned_1": "0.000",
                "electricity_delivered_2": "1484.761",
                "electricity_returned_2": "0.000",
                "electricity_currently_delivered": "0.075",
                "electricity_currently_returned": "0.000",
                "phase_currently_delivered_l1": "0.017",
                "phase_currently_delivered_l2": "0.058",
                "phase_currently_delivered_l3": "0.000",
                "phase_currently_returned_l1": "0.000",
                "phase_currently_returned_l2": "0.000",
                "phase_currently_returned_l3": "0.000",
                "extra_device_timestamp": "2017-01-31T22:00:00Z",
                "extra_device_delivered": "1835.904"
            },
            ... <MORE RESULTS> ...
        ]
    }
    
    
.. warning::

    Please note that all timestamps **returned** are in **UTC (CET -1 / CEST -2)**. This is indicated as well by the timestamps ending with a 'Z' (Zulu timezone).


----


``GET`` - ``/datalogger/meter-statistics``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retrieve meter statistics.

.. note::

    This endpoint was added in DSMR-reader ``v3.1``


URI
~~~
Full path: ``/api/v2/datalogger/meter-statistics``


Parameters
~~~~~~~~~~
None.


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the data in JSON format. Any other status code on failure.


Example
~~~~~~~

Using **cURL** (commandline)::

    # Don't forget to replace 'YOUR-DSMR-URL' and 'YOUR-API-KEY' with your own values.
    curl http://YOUR-DSMR-URL/api/v2/datalogger/meter-statistics \
          -H 'Authorization: Token YOUR-API-KEY' | python -m json.tool


**Result**::

    {
        "id": 1,
        "timestamp": "2020-01-15T20:13:40+01:00",
        "dsmr_version": "40",
        "electricity_tariff": 1,
        "power_failure_count": 3,
        "long_power_failure_count": 0,
        "voltage_sag_count_l1": 1,
        "voltage_sag_count_l2": 2,
        "voltage_sag_count_l3": 3,
        "voltage_swell_count_l1": 0,
        "voltage_swell_count_l2": 0,
        "voltage_swell_count_l3": 0,
        "rejected_telegrams": 99,
        "latest_telegram": "/XMX5LGBBFFB123456789\r\n\r\n1-3:0.2.8(40)\r\n0-0:1.0.0(200115201340W)\r\n0-0:96.1.1(12345678901234567890123456789000)\r\n1-0:1.8.1(007952.261*kWh)\r\n1-0:2.8.1(000000.000*kWh)\r\n1-0:1.8.2(004771.357*kWh)\r\n1-0:2.8.2(000000.000*kWh)\r\n0-0:96.14.0(0001)\r\n1-0:1.7.0(02.507*kW)\r\n1-0:2.7.0(00.000*kW)\r\n0-0:96.7.21(00003)\r\n0-0:96.7.9(00000)\r\n1-0:99.97.0(0)(0-0:96.7.19)\r\n1-0:32.32.0(00001)\r\n1-0:52.32.0(00002)\r\n1-0:72.32.0(00003)\r\n1-0:32.36.0(00000)\r\n1-0:52.36.0(00000)\r\n1-0:72.36.0(00000)\r\n0-0:96.13.1()\r\n0-0:96.13.0()\r\n1-0:32.7.0(225.0*V)\r\n1-0:52.7.0(232.1*V)\r\n1-0:72.7.0(233.2*V)\r\n1-0:31.7.0(000*A)\r\n1-0:51.7.0(000*A)\r\n1-0:71.7.0(001*A)\r\n1-0:21.7.0(01.407*kW)\r\n1-0:41.7.0(00.765*kW)\r\n1-0:61.7.0(00.334*kW)\r\n1-0:22.7.0(00.000*kW)\r\n1-0:42.7.0(00.000*kW)\r\n1-0:62.7.0(00.000*kW)\r\n!013B"
    }


.. warning::

    Please note that all timestamps **returned** are in **UTC (CET -1 / CEST -2)**. This is indicated as well by the timestamps ending with a 'Z' (Zulu timezone).


----


``PATCH`` - ``/datalogger/meter-statistics``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Manually updates any meter statistics fields.

.. note::

    This endpoint was added in DSMR-reader ``v3.1``


.. warning::

    You should **not use this if you're using the v1 datalogger to push your telegrams**, as they will collide and overwrite each other's data!


URI
~~~
Full path: ``/api/v2/datalogger/meter-statistics``


Parameters
~~~~~~~~~~
Since this is a ``PATCH`` operation, **all parameters are optional**.

- ``timestamp`` (*datetime*) - Timestamp indicating the last update. The builtin datalogger uses the timestamp of the telegram for this.
- ``dsmr_version`` (*string*) - DSMR protocol version string. Should be something like ``42`` (4.2) or ``50`` (5.0)
- ``power_failure_count`` (*int*) - Number of power failures in any phase
- ``long_power_failure_count`` (*int*) - Number of long power failures in any phase
- ``voltage_sag_count_l1`` (*int*) - Number of voltage sags/dips in phase L1
- ``voltage_sag_count_l2`` (*int*) - Number of voltage sags/dips in phase L2 (polyphase meters only)
- ``voltage_sag_count_l3`` (*int*) - Number of voltage sags/dips in phase L3 (polyphase meters only)
- ``voltage_swell_count_l1`` (*int*) - Number of voltage swells in phase L1
- ``voltage_swell_count_l2`` (*int*) - Number of voltage swells in phase L2 (polyphase meters only)
- ``voltage_swell_count_l3`` (*int*) - Number of voltage swells in phase L3 (polyphase meters only)
- ``rejected_telegrams`` (*int*) - Number of rejected telegrams due to invalid CRC checksum
- ``latest_telegram`` (*string*) - The latest telegram succesfully read

All parameters, except for ``timestamp`` and ``rejected_telegrams`` are **nullable**. Send an empty value to make them ``null``.

.. note::

    **datetime format** = ``YYYY-MM-DDThh:mm[:ss][+HH:MM|-HH:MM|Z]``, i.e.: ``2017-01-01T12:00:00+01`` (CET), ``2017-04-15T12:00:00+02`` (CEST) or ``2017-04-15T100:00:00Z`` (UTC).


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the updated data in JSON format. Any other status code on failure.


Example
~~~~~~~
**Data** to update::

    timestamp: 2020-01-15T12:34:56+01
    dsmr_version: '50'
    power_failure_count: 1
    voltage_sag_count_l1: 5
    voltage_swell_count_l1: 6
    latest_telegram: null


Using **cURL** (commandline)::

    # Don't forget to replace 'YOUR-DSMR-URL' and 'YOUR-API-KEY' with your own values.
    # Please note that the plus symbol "+" has been replaced by "%2B" here, to make it work for cURL.
    curl --request PATCH http://YOUR-DSMR-URL/api/v2/datalogger/meter-statistics \
          -d 'timestamp=2020-01-15T12:34:56%2B01&dsmr_version=50&power_failure_count=1&voltage_sag_count_l1=5&voltage_swell_count_l1=6&latest_telegram=' \
          -H 'Authorization: Token YOUR-API-KEY' | python -m json.tool


Using **requests** (Python)::

    import requests
    import json

    response = requests.patch(
        'http://YOUR-DSMR-URL/api/v2/datalogger/meter-statistics',
        headers={'Authorization': 'Token YOUR-API-KEY'},
        data={
            'timestamp': '2020-01-15T12:34:56+01'
            'dsmr_version': '50'
            'power_failure_count': 1
            'voltage_sag_count_l1': 5
            'voltage_swell_count_l1': 6
            'latest_telegram': None
        }
    )

    if response.status_code != 200:
        print('Error: {}'.format(response.text))
    else:
        print('Updated: {}'.format(json.loads(response.text)))


**Result**::

    {
        "id": 1,
        "timestamp": "2020-01-15T12:34:56+01:00",
        "dsmr_version": "50",
        "electricity_tariff": 1,
        "power_failure_count": 1,
        "long_power_failure_count": 0,
        "voltage_sag_count_l1": 5,
        "voltage_sag_count_l2": 2,
        "voltage_sag_count_l3": 3,
        "voltage_swell_count_l1": 6,
        "voltage_swell_count_l2": 0,
        "voltage_swell_count_l3": 0,
        "rejected_telegrams": 99,
        "latest_telegram": null
    }


----

    
``GET`` - ``consumption/electricity``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Retrieves any data regarding **electricity consumption**. This is based on the readings processed.


URI
~~~
Full path: ``/api/v2/consumption/electricity``


Parameters
~~~~~~~~~~
All parameters are optional.

- ``read_at__gte`` (*datetime*) - Limits the result to any records having a timestamp **higher or equal** to this parameter.
- ``read_at__lte`` (*datetime*) - Limits the result to any records having a timestamp **lower or equal** to this parameter.
- ``ordering`` (*string*) - Use ``-read_at`` to sort **descending**. Omit or use ``read_at`` to sort **ascending** (default).
- ``offset`` (*integer*) - When iterating large resultsets, the offset determines the starting point.
- ``limit`` (*integer*) - Limits the resultset size returned. Omit for maintaining the default limit (**25**).


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~
**Data structure returned**::

    {
        "count": 96940,
        "next": "http://YOUR-DSMR-URL/api/v2/consumption/electricity?offset=2",
        "previous": null,
	    "results": [
	        {
	            "id": 1728715,
	            "read_at": "2019-04-19T10:58:00+02:00",
	            "delivered_1": "3332.442",
	            "returned_1": "0.000",
	            "delivered_2": "3441.996",
	            "returned_2": "0.000",
	            "currently_delivered": "0.147",
	            "currently_returned": "0.000",
	            "phase_currently_delivered_l1": "0.013",
	            "phase_currently_delivered_l2": "0.133",
	            "phase_currently_delivered_l3": "0.000",
	            "phase_currently_returned_l1": "0.000",
	            "phase_currently_returned_l2": "0.000",
	            "phase_currently_returned_l3": "0.000"
	        },
            ... <MORE RESULTS> ...
	    ]
    }


----
    
    
``GET`` - ``consumption/gas``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Retrieves any data regarding **gas consumption**. This is based on the readings processed.


URI
~~~
Full path: ``/api/v2/consumption/gas``


Parameters
~~~~~~~~~~
All parameters are optional.

- ``read_at__gte`` (*datetime*) - Limits the result to any records having a timestamp **higher or equal** to this parameter.
- ``read_at__lte`` (*datetime*) - Limits the result to any records having a timestamp **lower or equal** to this parameter.
- ``ordering`` (*string*) - Use ``-read_at`` to sort **descending**. Omit or use ``read_at`` to sort **ascending** (default).
- ``offset`` (*integer*) - When iterating large resultsets, the offset determines the starting point.
- ``limit`` (*integer*) - Limits the resultset size returned. Omit for maintaining the default limit (**25**).


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~
**Data structure returned**::

    {
        "count": 28794,
        "next": "http://YOUR-DSMR-URL/api/v2/consumption/gas?offset=2",
        "previous": null,
	    "results": [
	        {
	            "id": 28858,
	            "read_at": "2019-04-19T09:00:00+02:00",
	            "delivered": "2850.598",
	            "currently_delivered": "0.060"
	        },
            ... <MORE RESULTS> ...
	    ]
    }

    
----
    

``GET`` - ``consumption/today``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Returns the consumption of the current day so far.


URI
~~~
Full path: ``/api/v2/consumption/today``


Parameters
~~~~~~~~~~
None.


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~

**Data structure returned**::

    {
        "day": "2017-09-28",
        "electricity1": 0.716,
        "electricity1_cost": 0.12,
        "electricity1_returned": 0,
        "electricity2": 3.403,
        "electricity2_cost": 0.63,
        "electricity2_returned": 0,
        "gas": 0.253,
        "gas_cost": 0.15,
        "total_cost": 0.9,
    }

    
----
    

``GET`` - ``consumption/electricity-live``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Returns the live electricity consumption, containing the same data as the Dashboard header.


URI
~~~
Full path: ``/api/v2/consumption/electricity-live``


Parameters
~~~~~~~~~~
None.


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~

**Note**: ``cost_per_hour`` is only available when you've set energy prices.

**Data structure returned**::

    {
        "timestamp": "2016-07-01T20:00:00Z",
        "currently_returned": 0,
        "currently_delivered": 1123,
        "cost_per_hour": 0.02,
    }


    
----
    

``GET`` - ``consumption/gas-live``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Returns the latest gas consumption.


URI
~~~
Full path: ``/api/v2/consumption/gas-live``


Parameters
~~~~~~~~~~
None.


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~

**Note**: ``cost_per_interval`` is only available when you've set energy prices.

**Data structure returned**::

    {
        "timestamp": "2019-04-19T00:00:00Z",
        "currently_delivered": 0.456,
        "cost_per_interval": 0.34,
    }


----
    
    
``GET`` - ``statistics/day``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Retrieves any **aggregated day statistics**. Please note that these are generated a few hours **after midnight**.


URI
~~~
Full path: ``/api/v2/statistics/day``


Parameters
~~~~~~~~~~
All parameters are optional.

- ``day__gte`` (*date*) - Limits the result to any statistics having their date **higher or equal** to this parameter.
- ``day__lte`` (*date*) - Limits the result to any statistics having their date **lower or equal** to this parameter.
- ``ordering`` (*string*) - Use ``-day`` to sort **descending**. Omit or use ``day`` to sort **ascending** (default).
- ``offset`` (*integer*) - When iterating large resultsets, the offset determines the starting point.
- ``limit`` (*integer*) - Limits the resultset size returned. Omit for maintaining the default limit (**25**).


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~
All the :ref:`generic DSMRREADING examples <generic-examples-anchor>` apply here as well, since only the ``timestamp`` field differs.

**Data structure returned**::

    {
        "count": 29,
        "next": "http://YOUR-DSMR-URL/api/v2/statistics/day?day__gte=2017-02-01&day__lte=2017-03-01&limit=25&offset=25",
        "previous": null,
        "results": [
            {
                "id": 709,
                "day": "2017-02-25",
                "total_cost": "3.14",
                "electricity1": "7.289",
                "electricity2": "0.000",
                "electricity1_returned": "0.000",
                "electricity2_returned": "0.000",
                "electricity1_cost": "1.30",
                "electricity2_cost": "0.00",
                "gas": "3.047",
                "gas_cost": "1.84",
                "lowest_temperature": "0.6",
                "highest_temperature": "7.9",
                "average_temperature": "4.3"
            }
        ]
    }


----
    
    
``GET`` - ``statistics/hour``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Retrieves any **aggregated hourly statistics**. Please note that these are generated a few hours **after midnight**.


URI
~~~
Full path: ``/api/v2/statistics/hour``


Parameters
~~~~~~~~~~
All parameters are optional.

- ``hour_start__gte`` (*datetime*) - Limits the result to any statistics having their datetime (hour start) **higher or equal** to this parameter.
- ``hour_start__lte`` (*datetime*) - Limits the result to any statistics having their datetime (hour start) **lower or equal** to this parameter.
- ``ordering`` (*string*) - Use ``-hour_start`` to sort **descending**. Omit or use ``hour_start`` to sort **ascending** (default).
- ``offset`` (*integer*) - When iterating large resultsets, the offset determines the starting point.
- ``limit`` (*integer*) - Limits the resultset size returned. Omit for maintaining the default limit (**25**).


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~
All the :ref:`generic DSMRREADING examples <generic-examples-anchor>` apply here as well, since only the ``timestamp`` field differs.

**Data structure returned**::

    {
        "count": 673,
        "next": "http://YOUR-DSMR-URL/api/v2/statistics/hour?hour_start__gte=2017-02-01+00%3A00%3A00&hour_start__lte=2017-03-01+00%3A00%3A00&limit=25&offset=25",
        "previous": null,
        "results": [
            {
                "id": 12917,
                "hour_start": "2017-02-01T23:00:00Z",
                "electricity1": "0.209",
                "electricity2": "0.000",
                "electricity1_returned": "0.000",
                "electricity2_returned": "0.000",
                "gas": "0.886"
            }
        ]
    }


----


``GET`` - ``application/version``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Returns the version of DSMR-reader you are running.


URI
~~~
Full path: ``/api/v2/application/version``


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~

**Data structure returned**::

    {
        "version": "1.20.0",
    }




----


``GET`` - ``application/status``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Returns the status of DSMR-reader, containing the same data as displayed on the Status page.


URI
~~~
Full path: ``/api/v2/application/status``


Response
~~~~~~~~
``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure.


Example
~~~~~~~

**Data structure returned**::

    {
        "readings": {
            "latest": "2018-06-28T03:58:54Z",
            "unprocessed": {
                "count": 0,
                "seconds_since": null
            },
            "seconds_since": 47870
        },
        "gas": {
            "latest": "2018-06-28T02:00:00Z",
            "hours_since": 15
        },
        "capabilities": {
            "gas": true,
            "any": true,
            "weather": true,
            "electricity_returned": false,
            "electricity": true,
            "multi_phases": true
        },
        "electricity": {
            "latest": "2018-06-28T03:59:00Z",
            "minutes_since": 798
        },
        "statistics": {
            "latest": "2018-06-27",
            "days_since": 1
        }
    }
