Installation: Remote datalogger
###############################

.. note::

    This will install a datalogger that will forward telegrams to a remote instance of DSMR-reader, using its API.

.. contents:: :local:
    :depth: 1

The remote datalogger script has been overhauled in DSMR-reader ``v5.0``.
If you installed a former version, reconsider reinstalling it completely with the new version below.

.. attention::

    To be clear, there should be two hosts:

    - The device hosting the remote datalogger
    - The device (or server) hosting the receiving DSMR-reader instance

Receiving DSMR-reader instance
------------------------------

Make sure to first prepare the API at the DSMR-reader instance you'll forward the telegrams to.
You can enable the API and view/edit the API key used :doc:`in the configuration</tutorial/configuration>`.

.. hint::

    If your smart meter only supports DSMR v2 (or you are using a non Dutch smart meter), make sure to change the DSMR version :doc:`in the configuration</tutorial/configuration>` as well, to have DSMR-reader parse them correctly.

Also, you should disable the datalogger process over there, since you won't be using it anyway::

    sudo rm /etc/supervisor/conf.d/dsmr_datalogger.conf
    sudo supervisorctl reread
    sudo supervisorctl update

Remote datalogger device
------------------------

Switch to the device you want to install the remote datalogger on.

Execute::

    # Packages
    sudo apt-get install -y supervisor python3 python3-pip python3-virtualenv virtualenvwrapper

    # System user
    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash
    sudo usermod -a -G dialout dsmr
    sudo chown -R dsmr:dsmr /home/dsmr/

    # Virtual env
    sudo -u dsmr mkdir /home/dsmr/.virtualenvs
    sudo -u dsmr virtualenv /home/dsmr/.virtualenvs/dsmrreader --system-site-packages --python python3
    sudo sh -c 'echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> /home/dsmr/.bashrc'

    # Requirements
    sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/pip3 install pyserial==3.5 requests==2.26.0 python-decouple==3.5


Datalogger script
^^^^^^^^^^^^^^^^^

Create a new file ``/home/dsmr/dsmr_datalogger_api_client.py`` with the following contents: `dsmr_datalogger_api_client.py on GitHub <https://github.com/dsmrreader/dsmr-reader/blob/v5/dsmr_datalogger/scripts/dsmr_datalogger_api_client.py>`_

Or execute the following to download it directly to the path above::

    sudo wget -O /home/dsmr/dsmr_datalogger_api_client.py https://raw.githubusercontent.com/dsmrreader/dsmr-reader/v5/dsmr_datalogger/scripts/dsmr_datalogger_api_client.py


API config (``.env``)
^^^^^^^^^^^^^^^^^^^^^

.. attention::

    Since DSMR-reader ``v5.x``, all env vars for this script were prefixed with ``REMOTE_``.
    E.g.: ``DATALOGGER_INPUT_METHOD`` is now ``REMOTE_DATALOGGER_INPUT_METHOD``.

    This only affects **new installations** of the script.

.. hint::

    The ``.env`` file below is not mandatory to use. Alternatively you can specify all settings mentioned below as system environment variables.

Create another file ``/home/dsmr/.env`` and add as contents::

    ### The DSMR-reader API('s) to forward telegrams to:
    REMOTE_DATALOGGER_API_HOSTS=
    REMOTE_DATALOGGER_API_KEYS=

Keep the file open for multiple edits / additions below.

Add the schema (``http://``/``https://``) and hostname/port to ``REMOTE_DATALOGGER_API_HOSTS``. Add the API key to ``REMOTE_DATALOGGER_API_KEYS``. For example::

    # Example with default port:
    REMOTE_DATALOGGER_API_HOSTS=http://12.34.56.78
    REMOTE_DATALOGGER_API_KEYS=1234567890ABCDEFGH

    # Example with non standard port, e.g. Docker:
    REMOTE_DATALOGGER_API_HOSTS=http://12.34.56.78:7777
    REMOTE_DATALOGGER_API_KEYS=0987654321HGFEDCBA

.. tip::

    Are you using the remote datalogger for multiple instances of DSMR-reader? Then use ``REMOTE_DATALOGGER_API_HOSTS`` and ``REMOTE_DATALOGGER_API_KEYS`` as comma separated lists::

        # Example with multiple DSMR-reader installations:
        REMOTE_DATALOGGER_API_HOSTS=http://12.34.56.78,http://87.65.43.21:7777
        REMOTE_DATALOGGER_API_KEYS=1234567890ABCDEFGH,0987654321HGFEDCBA

        ### API host "http://12.34.56.78"      uses API key "1234567890ABCDEFGH"
        ### API host "http://87.65.43.21:7777" uses API key "0987654321HGFEDCBA"


Serial port or network socket config?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Choose either ``A.`` or ``B.`` below.


A. Serial port (``.env``)
^^^^^^^^^^^^^^^^^^^^^^^^^
Are you using a cable to read telegrams directly from a serial port?

Then add the following contents to ``/home/dsmr/.env``::

    REMOTE_DATALOGGER_INPUT_METHOD=serial
    REMOTE_DATALOGGER_SERIAL_PORT=/dev/ttyUSB0

    # DSMR meter version 4/5
    REMOTE_DATALOGGER_SERIAL_BAUDRATE=115200
    REMOTE_DATALOGGER_SERIAL_BYTESIZE=8
    REMOTE_DATALOGGER_SERIAL_PARITY=N

When needing a different port or serial settings, change the values accordingly. E.g.: For an older smart meter::

    # DSMR meter version 2/3
    REMOTE_DATALOGGER_SERIAL_BAUDRATE=9600
    REMOTE_DATALOGGER_SERIAL_BYTESIZE=7
    REMOTE_DATALOGGER_SERIAL_PARITY=E


B. Network socket (``.env``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Are you using a network socket for reading the telegrams? E.g.: ``ser2net``.

Then add the following contents to ``/home/dsmr/.env``::

    REMOTE_DATALOGGER_INPUT_METHOD=ipv4
    REMOTE_DATALOGGER_NETWORK_HOST=
    REMOTE_DATALOGGER_NETWORK_PORT=

Set the hostname or IP address in ``REMOTE_DATALOGGER_NETWORK_HOST`` and the port in ``REMOTE_DATALOGGER_NETWORK_PORT``.


Other settings (``.env``)
^^^^^^^^^^^^^^^^^^^^^^^^^

These settings are **optional** but can be tweaked when required:

- ``REMOTE_DATALOGGER_TIMEOUT``: The timeout in seconds that applies to reading the serial port and/or writing to the DSMR-reader API. Omit to use the default value.

- ``REMOTE_DATALOGGER_SLEEP``: The time in seconds that the datalogger will pause after each telegram written to the DSMR-reader API. Omit to use the default value.

- ``REMOTE_DATALOGGER_DEBUG_LOGGING``: Set to ``true`` or ``1`` to enable verbose debug logging. Omit to disable. Warning: Enabling this logging for a long period of time on a Raspberry Pi may cause accelerated wearing of your SD card!

Supervisor
^^^^^^^^^^

.. hint::

    The following steps are also meant for the device you've just installed the remote datalogger on.

Create a new supervisor config in ``/etc/supervisor/conf.d/dsmr_remote_datalogger.conf`` with contents::

    [program:dsmr_remote_datalogger]
    command=/home/dsmr/.virtualenvs/dsmrreader/bin/python3 -u /home/dsmr/dsmr_datalogger_api_client.py
    pidfile=/var/tmp/dsmrreader--%(program_name)s.pid
    user=dsmr
    group=dsmr
    autostart=true
    autorestart=true
    startsecs=1
    startretries=100
    stopwaitsecs=20
    redirect_stderr=true
    stdout_logfile=/var/log/supervisor/%(program_name)s.log
    stdout_logfile_maxbytes=10MB
    stdout_logfile_backups=3


Have Supervisor reread and update its configs to initialize the process::

    sudo supervisorctl reread
    sudo supervisorctl update

The script should now forward telegrams to the API host(s) you specified.
