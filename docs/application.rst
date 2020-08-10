Setting up the application
==========================


.. contents::
    :depth: 2


Accessing the application
-------------------------
Now it's time to view the application in your browser to check whether the GUI works as well. Just enter the ip address or hostname of your RaspberryPi in your browser. 

Did you install using a monitor attached to the RaspberryPi and you don't know what address your device has? Just type ``ifconfig | grep addr`` and it should display an ip address, for example::

    eth0      Link encap:Ethernet  HWaddr b8:27:eb:f4:24:de  
              inet addr:192.168.178.150  Bcast:192.168.178.255  Mask:255.255.255.0
              inet addr:127.0.0.1  Mask:255.0.0.0

In this example the ip address is ``192.168.178.150``. If possible, you should assign a static ip address to your device in your router. This will make sure you will always be able to find the application at the same location.



Data preservation & backups
---------------------------

.. seealso::

    :doc:`More information can be found here<data_integrity>`.


Reboot test
-----------
You surely want to ``reboot`` your device and check whether everything comes up automatically again with ``sudo supervisorctl status``. This will make sure your data logger 'survives' any power surges.


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

- Enable password protection :doc:`in the configuration<configuration>` for the entire application, available since DSMR-reader ``v4.0``.

- Install a firewall, such as ``ufw`` `UncomplicatedFirewall <https://wiki.ubuntu.com/UncomplicatedFirewall>`_ and restrict traffic to port ``22`` (only for yourself) and port ``80``.

- Use TLS (HTTPS) when possible.
