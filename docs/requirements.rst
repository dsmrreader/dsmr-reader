Requirements
============


.. contents::
    :depth: 2


OS: ``Raspbian OS``
^^^^^^^^^^^^^^^^^^^

*(Or similar. Raspbian is recommended and tested with, but any satisfying the requirements should do fine)*

.. note::

    - **Alternative #1**: You can also run it on any server near your smart meter, as long as it satisfies the other requirements.
    
    - **Alternative #2**: The application supports receiving P1 telegrams using an API, so you can also run it on a server outside your home. (:doc:`API docs here<api>`)


Hardware: ``RaspberryPi 3 or Linux server``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    The RaspberryPi 1 and 2 tend to be **too slow** for this project, as it requires multi core processing.
    
    You can however run just the datalogger client on an old RaspberryPi, :doc:`see for the API for a howto and example scripts<api>`.



Python: ``3.5+``
^^^^^^^^^^^^^^^^

.. warning::

    - Support for ``Python 3.3`` has been **discontinued** since ``DSMR-reader v1.5`` (due to Django).
    - Support for ``Python 3.4`` will be **discontinued** ``late 2018/begin 2019`` (due to Django & Python ``3.4`` End of Life).


Database: ``PostgreSQL 9+``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Support for ``MySQL`` has been **deprecated** since ``DSMR-reader v1.6`` and will be discontinued completely in a later release.
    Please use a PostgreSQL database instead.


Disk space: ``1+ GB``
^^^^^^^^^^^^^^^^^^^^^

*(For application installation & virtualenv)*

 - More disk space is required for storing all reader data captured (optional). I generally advise to use an 8+ GB SD card, depending on whether you keep all readings stored.
 - The readings will take about 90+ percent of the disk space used by the application. You can enable retention to have all readings cleaned up periodically. This will make the application barely use any disk space at all (depending on your settings).


P1 telegram cable
^^^^^^^^^^^^^^^^^

- **Smart Meter** with support for **at least DSMR 4.x+** and a **P1 telegram port**

-  **Smart meter P1 data cable** *(Can be purchased online and they cost around EUR 15,- to 20,-)*
