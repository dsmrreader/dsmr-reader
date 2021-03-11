Setting up the application
==========================


.. contents::
    :depth: 2


Accessing
---------
Now it's time to view the application in your browser to check whether the GUI works as well. Just enter the ip address or hostname of your RaspberryPi in your browser. 

Did you install using a monitor attached to the RaspberryPi and you don't know what address your device has? Just type ``ifconfig | grep addr`` and it should display an ip address, for example::

    eth0      Link encap:Ethernet  HWaddr b8:27:eb:f4:24:de  
              inet addr:192.168.178.150  Bcast:192.168.178.255  Mask:255.255.255.0
              inet addr:127.0.0.1  Mask:255.0.0.0

In this example the ip address is ``192.168.178.150``. If possible, you should assign a static ip address to your device in your router. This will make sure you will always be able to find the application at the same location.


Reboot test
-----------
You surely want to ``reboot`` your device and check whether everything comes up automatically again with ``sudo supervisorctl status``. This will make sure your data logger 'survives' any power surges.


Public webinterface warning
---------------------------

.. warning::

    If you expose your application to the outside world or a public network, you might want to take additional steps:

- Enable password protection :doc:`in the configuration<configuration>` for the entire application, available since DSMR-reader ``v4.0``.

- Install a firewall, such as ``ufw`` `UncomplicatedFirewall <https://wiki.ubuntu.com/UncomplicatedFirewall>`_ and restrict traffic to port ``22`` (only for yourself) and port ``80``.

- Use TLS (HTTPS) when possible.


Data integrity
--------------

.. warning::

    Read this section carefully if you are using any volatile storage, such as an SD card.


Storage
^^^^^^^
This project was designed to run on a RaspberryPi, but it affects the lifetime of the storage severely.
The introduction of DSMR v5 smart meters strains the storage even more, due to the high amount of telegrams sent each second.

The default storage on RaspberryPi's suffers greatly from this and can not be trusted to keep your data safe.
Eventually the storage will get corrupted and either make your data inaccessible, or it pretends to write data, while not storing anything at all.

Reducing the data throughput may help as well. :doc:`More information can be found in the FAQ (data section)<../reference/faq>`.


Backups
^^^^^^^
DSMR-reader does support automated backups, but since they are still stored on the same volatile storage, they can be corrupted as well.

By default backups are created and written to::

    /home/dsmr/dsmr-reader/backups/


Prevention
^^^^^^^^^^
The only thing you can do, is make sure to have your backups stored somewhere else, once in a while.
Using Dropbox to sync your backups does not protect them of all harm!

.. note::

    If you are more technical savy, you could opt to either install the database or the entire application on a server with storage that tends to wear less.
    You can use the RaspberryPi are a remote datalogger, preventing a lot of issues.

    :doc:`More information about using a remote datalogger here<../how-to/installation/remote-datalogger>`.


Pitfalls
^^^^^^^^
- SD cards' lifespan in this project vary from several weeks to some years, depending on the quality of the storage and the interval of telegrams sent by you smart meter.
- Backups are created daily, but rotated weekly! So it's possible that, at some point, the backups get corrupted as well since they're overwritten each week. And eventually they will get synchronized to Dropbox as well.
