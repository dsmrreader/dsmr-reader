Env Settings
============

You can either specify the following settings as system environments variables or define them in a ``.env`` file in the root of the DSMR-reader project folder.

.. contents::


``SECRET_KEY``
~~~~~~~~~~~~~~
**Required**

The secret key Django should use. This should be randomly generated for your installation.
Generate or refresh it by running ``./tools/generate-secret-key.sh``.


``DB_ENGINE``
~~~~~~~~~~~~~
**Required**

The database engine to use. Officially DSMR-reader only supports ``django.db.backends.postgresql``, but others supported by Django may work as well.
Experiment at your own risk!


``DB_NAME``
~~~~~~~~~~~
The database name to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.


``DB_USER``
~~~~~~~~~~~
The database user to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.


``DB_PASS``
~~~~~~~~~~~
The database password for the ``DB_USER`` to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.


``DB_HOST``
~~~~~~~~~~~
The database host to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.


``DB_PORT``
~~~~~~~~~~~
The database port to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.


``DSMR_USER``
~~~~~~~~~~~~~
**Situational**

The username of the **webinterface** (super)user to create when running ``./manage.py dsmr_superuser``.


``DSMR_PASSWORD``
~~~~~~~~~~~~~~~~~
**Situational**

The password of the ``DSMR_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.


``DSMRREADER_LOGLEVEL``
~~~~~~~~~~~~~~~~~~~~~~~
**Optional**

The log level DSMR-reader should use. Choose either ``ERROR`` (omit for this default) or ``DEBUG`` (should be temporary due to file I/O).

For more information, :doc:`see Troubleshooting<troubleshooting>`.


``DSMRREADER_PLUGINS``
~~~~~~~~~~~~~~~~~~~~~~~
**Optional**

The plugins DSMR-reader should use. Omit to use the default of no plugins.
Note that this should be a comma separated list when specifying multiple plugins. E.g.::

    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1
    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1,dsmr_plugins.modules.plugin_name2

For more information, :doc:`see Plugins<plugins>`.


``CONN_MAX_AGE``
~~~~~~~~~~~~~~~~
**Optional**

The max lifetime for the database connections. Omit to use the default.


``TZ``
~~~~~~
**Optional**

The timezone Django should use. Alter at your own risk. Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands).
