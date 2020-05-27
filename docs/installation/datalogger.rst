Installation: Datalogger only
=============================

This will install a datalogger that will forward telegrams to another fully installed instance of DSMR-reader, using its API.

To be clear, there should be two hosts:

- The device hosting the datalogger
- The device (or server) hosting the receiving DSMR-reader instance

Receiving DSMR-reader instance: preparation
-------------------------------------------

Make sure to prepare the API at the DSMR-reader instance you'll forward the telegrams to.
For more information configuring it, :doc:`see the API settings <../admin/api>`.

.. warning::

    If your smart meter only supports DSMR v2, make sure to change the DSMR version :doc:`in the datalogger settings <../admin/datalogger>`.

Also, you should disable the datalogger process over there, since you won't be using it anyway::

    # On the DSMR-reader instance you'll forward the telegrams to.

    sudo rm /etc/supervisor/conf.d/dsmr_datalogger.conf
    sudo supervisorctl reread
    sudo supervisorctl update

Datalogger instance: installation
---------------------------------

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

    # Requirements
    sudo sudo -u dsmr /home/dsmr/.virtualenvs/dsmrreader/bin/pip3 install pyserial==3.4 pyserial-asyncio==0.4 requests==2.22.0


Datalogger instance: Script
---------------------------

Create a new file ``/home/dsmr/dsmr_datalogger_api_client.py`` with this content: `dsmr_datalogger_api_client.py on GitHub <https://github.com/dennissiemensma/dsmr-reader/blob/v3/dsmr_datalogger/scripts/dsmr_datalogger_api_client.py>`_

.. note::

    The serial connection in the script above is based on ``DSMR v4/v5``. When required, change these in ``SERIAL_SETTINGS`` in the script.

.. warning::

    Don't forget to insert your own API URL and API key as defined in ``API_SERVERS`` in the script.

Datalogger instance: Supervisor
-------------------------------

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


Update and run **Supervisor**::

    sudo supervisorctl reread
    sudo supervisorctl update


The script should now forward telegrams to the API URL you specified.

.. note::

    If you make any changes to the script later, make sure to restart it with: ``sudo supervisorctl update``