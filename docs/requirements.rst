Requirements
============


.. contents::
    :depth: 2


OS / hardware
^^^^^^^^^^^^^
**Raspbian OS or Debian based OS**

 - Recommended and tested with, but any OS satisfying the requirements should do fine.

.. note::

    - **Alternative #1**: You can also run it on any server near your smart meter, as long as it satisfies the other requirements.
    
    - **Alternative #2**: The application supports receiving P1 telegrams using an API, so you can also run it on a server outside your home. (:doc:`API DOCS<api>`)


**RaspberryPi 3 or Linux server**


.. warning::

    The RaspberryPi 1 and 2 tend to be **too slow** for this project, as it requires multi core processing.
    
    You can however run just the datalogger client on an old RaspberryPi, :doc:`see for the API for a howto and example scripts<api>`.



Python
^^^^^^

**Python 3.4+**

.. warning::

    Support for ``Python 3.3`` has been **discontinued** since ``DSMR-reader v1.5`` (due to Django).


Database
^^^^^^^^

**PostgreSQL 9+**

.. warning::

    Support for ``MySQL`` has been **deprecated** since ``DSMR-reader v1.6`` and will be discontinued completely in a later release.
    Please use a PostgreSQL database instead. Users already running MySQL will be supported in migrating at a later moment.


Disk space
^^^^^^^^^^

**Minimal 1 GB of disk space on RaspberryPi (card)** (for application installation & virtualenv). 

 - More disk space is required for storing all reader data captured (optional). I generally advise to use a 8+ GB SD card. 
 - The readings will take about 90+ percent of the disk space. Retention is on it's way for a future release in 2017. 


Cable
^^^^^

**Smart Meter** with support for **at least DSMR 4.x+** and a **P1 telegram port**

 - Tested so far with Landis+Gyr E350, Kaifa.

**Smart meter P1 data cable** 

 - Can be purchased online and they cost around 15 tot 20 Euro's each.


Misc
^^^^

**Basic Linux knowledge for deployment, debugging and troubleshooting**

 - It just really helps if you know what you are doing.

