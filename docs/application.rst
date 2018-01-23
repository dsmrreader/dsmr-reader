Using the application
=====================


.. contents::
    :depth: 2


DSMR 2.x (legacy)
-----------------

.. note::
    
    Note: The application's default DSMR version used is 4.x. This version is also the **default** for any recent smart meters placed at your home. 

.. warning::
    
    Make sure to alter this setting in the backend's configuration page to DSMR 2.x when required!


Viewing the application
-----------------------
Now it's time to view the application in your browser to check whether the GUI works as well. Just enter the ip address or hostname of your RaspberryPi in your browser. 

Did you install using a monitor attached to the RaspberryPi and you don't know what address your device has? Just type ``ifconfig | grep addr`` and it should display an ip address, for example::

    eth0      Link encap:Ethernet  HWaddr b8:27:eb:f4:24:de  
              inet addr:192.168.178.150  Bcast:192.168.178.255  Mask:255.255.255.0
              inet addr:127.0.0.1  Mask:255.0.0.0

In this example the ip address is ``192.168.178.150``. If possible, you should assign a static ip address to your device in your router. This will make sure you will always be able to find the application at the same location.


Reboot test
-----------
You surely want to ``reboot`` your device and check whether everything comes up automatically again with ``sudo supervisorctl status``. This will make sure your data logger 'survives' any power surges.


Data preservation & backups
---------------------------

.. note::

    You **should (or must)** make sure to periodically BACKUP your data! It's one of the most common mistakes to skip or ignore this.
    Actually, it happened to myself quite soon after I started, as I somehow managed to corrupt my SD storage card, losing all my data on it.
    It luckily happened only a month after running my own readings, but imagine all the data you'll lose when it will contain readings taken over several years.

- The SD card is by far **the weakest link** of this setup and **will** fail you some day.

- The application will, by default, create a database backup every night. 

 - You can find them in the ``backups`` folder of the application. They either have a ``.sql`` or ``.gz`` extension, depending on whether compression is enabled in the backup configuration.
 - However, as the data is still stored **locally** on your 'vulnerable' SD card, you must export it off your RaspberryPi as well. 

- There is an builtin option to have backups synced to your **Dropbox**, *without exposing your Dropbox account and your private files in it*. 

 - Please either use this service or manage offloading backups on your own (see below).

- You may also decide to run backups outside the application. 

 - There are example backup scripts available in ``dsmrreader/provisioning/postgresql/psql-backup.sh`` for **PostgreSQL**, which I dump to a separately USB stick mounted on my RaspberryPi. 

 - For **MySQL/MariaDB** you can use ``dsmrreader/provisioning/mysql/mysql-backup.sh``.
 
 - Make sure to schedule the backup scripts as cronjob and also verify that it actually works, by running ``run-parts -v /etc/cron.daily``.

- Also, check your free disk space once in a while. I will implement automatic cleanup settings later, allowing you to choose your own retention (for all the source readings).

Everything OK? Congratulations, this was the hardest part and now the fun begins by monitoring your energy consumption.


Optional: Setting up an USB drive for backups
---------------------------------------------

.. seealso::
    
    For more information about (optionally) setting up an USB drive for backups, see `Data preservation/backups #268 <https://github.com/dennissiemensma/dsmr-reader/issues/268>`_.



Application updates (bug fixes & new features)
----------------------------------------------

.. seealso::
    
    :doc:`This information can be found here<faq>`.


Public webinterface warning
---------------------------

.. warning::

    If you expose your application to the outside world or a public network, you might want to take additional steps:

- Please make sure to **alter** the ``SECRET_KEY`` setting in your ``dsmrreader/settings.py``.

 - Don't forget to run ``./post-deploy.sh`` in the project's root, which will force the application to gracefully reload itself and apply the new settings instantly.

- Install a firewall, such as ``ufw`` `UncomplicatedFirewall <https://wiki.ubuntu.com/UncomplicatedFirewall>`_ and restrict traffic to port ``22`` (only for yourself) and port ``80``.

- You should also have Nginx restrict application access when exposing it to the Internet. Simply generate an htpasswd string `using one of the many generators found online <https://www.transip.nl/htpasswd/>`_. 

- Paste the htpasswd string in ``/etc/nginx/htpasswd``.

.. warning::
    
    It's safe to a htpasswd generator, **just make sure to NEVER enter personal credentials** there **used for other applications or personal accounts**.
    
.. seealso::
    
    Alternatively you can generate a ``htpasswd`` file locally, by installing ``sudo apt-get install apache2-utils`` and running ``sudo htpasswd -c /etc/nginx/htpasswd USERNAME`` (where ``USERNAME`` is your desired username).
    
    The command will prompt you to enter a password for it. 


- Open the site's vhost in ``/etc/nginx/sites-enabled/dsmr-webinterface`` and **uncomment** the following lines (remove the ##)::

    ##    auth_basic "Restricted application";
    ##    auth_basic_user_file /etc/nginx/htpasswd;
    
- Now make sure you didn't insert any typo's by running::

    sudo service nginx configtest
    
- And reload with::

    sudo service nginx reload 

You should be prompted for login credentials the next time your browser accesses the application. For more information regarding this topic, see the `Nginx docs <https://www.nginx.com/resources/admin-guide/restricting-access/>`_.
