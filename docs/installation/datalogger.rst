Installation: Datalogger only
=============================

This will install a datalogger that will forward telegrams to another fully installed instance of DSMR-reader, using its API.


Prepare API
-----------

Make sure to prepare the API at the DSMR-reader instance you'll forward the telegrams to.
For more information configuring it, :doc:`see the API settings <../admin/api>`.

.. warning::

    If your smart meter only supports DSMR v2, make sure to change the DSMR version :doc:`in the datalogger settings <../admin/datalogger>`.


Installation
------------

Execute::

    # Packages
    sudo apt-get install -y supervisor python3 python3-pip python3-virtualenv virtualenvwrapper
    
    # System user
    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash
    sudo usermod -a -G dialout dsmr
    sudo chown -R dsmr:dsmr /home/dsmr/
    
    # Virtual env
    sudo sudo -u dsmr mkdir /home/dsmr/.virtualenvs
    sudo sudo -u dsmr virtualenv /home/dsmr/.virtualenvs/dsmrreader --no-site-packages --python python3
    sudo sh -c 'echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> /home/dsmr/.bashrc'
    sudo sh -c 'echo "cd ~/dsmr-reader" >> /home/dsmr/.bashrc'
    
    # Requirements
    sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/pip3 install pyserial==3.2.1 requests==2.12.4


Script
------

Create a new file: ``/home/dsmr/dsmr_datalogger_api_client.py`` with contents::

    from time import sleep

    from serial.serialutil import SerialException
    import requests
    import serial


    SLEEP = 0.5
    API_SERVERS = (
        ('http://HOST-OR-IP-ONE/api/v1/datalogger/dsmrreading', 'APIKEY-BLABLABLA-ABCDEFGHI'),
    ###    ('http://HOST-OR-IP-TWO/api/v1/datalogger/dsmrreading', 'APIKEY-BLABLABLA-JKLMNOPQR'),
    )


    def main():
        print ('Starting...')

        for telegram in read_telegram():
            print('Telegram read')

            for current_server in API_SERVERS:
                api_url, api_key = current_server

                print('Sending telegram to:', api_url)
                send_telegram(telegram, api_url, api_key)

            sleep(SLEEP)


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

        serial_handle.open()

        telegram_start_seen = False
        buffer = ''

        while True:
            try:
                data = serial_handle.readline()
            except SerialException as error:
                # Something else and unexpected failed.
                print('Serial connection failed:', error)
                return  # Break out of yield.

            try:
                # Make sure weird characters are converted properly.
                data = str(data, 'utf-8')
            except TypeError:
                pass

            # This guarantees we will only parse complete telegrams. (issue #74)
            if data.startswith('/'):
                telegram_start_seen = True

                # But make sure to RESET any data collected as well! (issue #212)
                buffer = ''

            # Delay any logging until we've seen the start of a telegram.
            if telegram_start_seen:
                buffer += data

            # Telegrams ends with '!' AND we saw the start. We should have a complete telegram now.
            if data.startswith('!') and telegram_start_seen:
                yield buffer

                # Reset the flow again.
                telegram_start_seen = False
                buffer = ''


    def send_telegram(telegram, api_url, api_key):
        # Forward telegram by simply sending it to the application with a POST request.
        response = requests.post(
            api_url,
            headers={'X-AUTHKEY': api_key},
            data={'telegram': telegram},
        )

        # Older versions of DSMR-reader return 200, recent installations do 201.
        if response.status_code not in (200, 201):
            # Or you will find the error (hint) in the reponse body on failure.
            print('API error: {}'.format(response.text))

    if __name__ == '__main__':
        main()



.. note::

    The serial connection in the script above is based on ``DSMR v4/v5``

.. warning::

    Don't forget to insert your own API URL and API key in the script above, in ``API_SERVERS``

Supervisor
----------

Create a new supervisor config in ``/etc/supervisor/conf.d/dsmr-client.conf`` with contents::

    [program:dsmr_client_datalogger]
    command=/usr/bin/nice -n 5 /home/dsmr/.virtualenvs/dsmrreader/bin/python3 -u /home/dsmr/dsmr_datalogger_api_client.py
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


Update and run **Supervisor**::

    sudo supervisorctl reread
    sudo supervisorctl update


The script should now forward telegrams to the API URL you specified.

.. note::

    If you make any changes to the script later, make sure to restart it with: ``sudo supervisorctl update``