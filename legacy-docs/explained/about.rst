About DSMR-reader
#################

.. contents::
    :depth: 3


Project goals
-------------
- Provide a tool to easily extract, store and visualize data transferred by the DSMR protocol of your smart meter.
- Allow you to export your data to other systems or third parties.

.. hint::

    **Data transfer protocol support**

    - **MQTT**: Push data from DSMR-reader to a generic message broker.
    - **REST API**: Push (telegram) data from a generic HTTP client to DSMR-reader.
    - **REST API**: Pull data from DSMR-reader from a generic HTTP client.

    Any integration should be possible this way, either using generic scripts or even :doc:`plugins</reference/plugins>`.
    DSMR-reader only supports the generic protocols above and cannot support every individual integration possible.


Architecture
------------

.. image:: ../_static/misc/DSMR-reader-Architecture.svg
    :target: ../_static/misc/DSMR-reader-Architecture.svg
    :alt: DSMR-reader Architecture


Languages
---------

The entire application and its code is written and documented in English.
The interface is translated into Dutch and will be enabled automatically, depending on your browser's language preference.


Hardware requirements
---------------------

- **For datalogger only**: *Any* RaspberryPi or similar.
- **For full DSMR-reader**: *RaspberryPi 4+* or similar.
- P1 telegram cable (or a network socket when using ``ser2net``).
- A smart meter supporting DSMR versions: ``v2`` / ``v4`` / ``v5``.


Software requirements
---------------------

- **OS**: ``RaspberryPi OS`` or similar (or using Docker).
- **Disk space**: 1+ GB - Depending on your smart meter and whether how many readings you want to preserve.
- **Code**: A `supported <https://devguide.python.org/versions/#python-release-cycle>`__ Python version.
- **Database**: A `supported <https://www.postgresql.org/support/versioning/>`__ PostgreSQL version.

Note that this project is built with `Django <https://www.djangoproject.com/>`__, which decides which Python/DB versions are actually supported.


Screenshots
-----------

Dashboard
^^^^^^^^^

The dashboard displays the latest information regarding the consumption of today.
You can view the total consumption for the current month and year as well.

If your meter supports it, you can also see your gas consumption and electricity returned.


.. image:: ../_static/screenshots/v5/frontend/dashboard.png
    :target: ../_static/screenshots/v5/frontend/dashboard.png
    :alt: Dashboard


Live graphs
^^^^^^^^^^^

The live graphs plots the most recent data available, depending on the capabilities of your smart meter.


.. image:: ../_static/screenshots/v5/frontend/live.png
    :target: ../_static/screenshots/v5/frontend/live.png
    :alt: Live graphs


Archive
^^^^^^^

The archive allows you to scroll through all historisch data captured by the application.
All data can be viewed on different levels: by day, by month and by year.


.. image:: ../_static/screenshots/v5/frontend/archive.png
    :target: ../_static/screenshots/v5/frontend/archive.png
    :alt: Archive


Compare
^^^^^^^

This page allows you to simply compare two days, months or years with each other.
It will also display the difference between each other as a percentage.

.. image:: ../_static/screenshots/v5/frontend/compare.png
    :target: ../_static/screenshots/v5/frontend/compare.png
    :alt: Compare


Trends
^^^^^^

This page displays a summary of your average daily consumption and habits.

.. image:: ../_static/screenshots/v5/frontend/trends.png
    :target: ../_static/screenshots/v5/frontend/trends.png
    :alt: Trends


Statistics
^^^^^^^^^^

This page displays your meter positions and statistics provided by the DSMR protocol.
You can also find the number of readings stored and any excesses regarding consumption.

.. image:: ../_static/screenshots/v5/frontend/statistics.png
    :target: ../_static/screenshots/v5/frontend/statistics.png
    :alt: Statistics


Energy contracts
^^^^^^^^^^^^^^^^

Summary of all your contracts and the amount of energy consumed/generated.

.. image:: ../_static/screenshots/v5/frontend/energy-contracts.png
    :target: ../_static/screenshots/v5/frontend/energy-contracts.png
    :alt: Energy contracts


Export
^^^^^^

This pages allows you to export all day or hour statistics to CSV.

.. image:: ../_static/screenshots/v5/frontend/export.png
    :target: ../_static/screenshots/v5/frontend/export.png
    :alt: Export


About
^^^^^

Shows the 'health' of the application. Any issues will be reported here.

You can also easily check for DSMR-reader updates here.

.. image:: ../_static/screenshots/v5/frontend/about.png
    :target: ../_static/screenshots/v5/frontend/about.png
    :alt: About


Support
^^^^^^^

Assists you in finding the information required for debugging your installation or any issues.

.. image:: ../_static/screenshots/v5/frontend/support.png
    :target: ../_static/screenshots/v5/frontend/support.png
    :alt: Support


Configuration
^^^^^^^^^^^^^

The configuration page is the entrypoint for the admin interface.

You can type any topic or setting you're searching for, as it should pop up with clickable deeplink to the admin panel.
Or you can just skip it this page and continue directly to the admin panel.


.. image:: ../_static/screenshots/v5/frontend/configuration.png
    :target: ../_static/screenshots/v5/frontend/configuration.png
    :alt: Configuration
