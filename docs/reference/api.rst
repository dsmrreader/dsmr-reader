API
===

The application has an API allowing you to insert/create readings and retrieve statistics.


.. contents::
    :depth: 2


Changelog
---------

.. versionadded:: 4.7.0

    - Added new endpoint to create day statistics

.. versionadded:: 4.4.0

    - Added new endpoint for application monitoring

.. versionchanged:: 4.0.0

    - Removed ``/api/v2/application/status``

.. deprecated:: 3.12

    - Deprecated ``/api/v2/application/status``


Documentation
-------------

.. hint::

    The API-documentation has been moved to your local installation since DSMR-reader ``v3.1``.

    You can access it by selecting the ``About & Support`` menu item in DSMR-reader.


Configuration
-------------

Enable API
^^^^^^^^^^

The API is disabled by default in the application. You may enable it :doc:`in the configuration</tutorial/configuration>`.

.. image:: ../_static/screenshots/v4/admin/apisettings.png
    :target: ../_static/screenshots/v4/admin/apisettings.png
    :alt: API admin settings

API key
^^^^^^^

A random API key is generated for you by default. You can always view or update it :doc:`in the configuration</tutorial/configuration>`.
