Env Settings
============

You can either specify the following settings as system environments variables or define them in a ``.env`` file in the root of the DSMR-reader project folder.

.. contents::


``SECRET_KEY``
~~~~~~~~~~~~~~
**Required**

The secret key Django should use. This should be randomly generated for your installation.
Generate or refresh it by running ``./tools/generate-secret-key.sh``.

See ``SECRET_KEY`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#secret-key>`__.


``DB_ENGINE``
~~~~~~~~~~~~~
**Required**

The database engine to use. Officially DSMR-reader only supports ``django.db.backends.postgresql``, but others supported by Django may work as well.
Experiment at your own risk!

See ``DATABASES.ENGINE`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#engine>`__.


``DB_NAME``
~~~~~~~~~~~
The database name to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.

See ``DATABASES.NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#name>`__.


``DB_USER``
~~~~~~~~~~~
The database user to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.

See ``DATABASES.USER`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#user>`__.


``DB_PASS``
~~~~~~~~~~~
The database password for the ``DB_USER`` to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.

See ``DATABASES.PASSWORD`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#password>`__.


``DB_HOST``
~~~~~~~~~~~
The database host to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.

See ``DATABASES.HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#host>`__.


``DB_PORT``
~~~~~~~~~~~
The database port to use.

**Required** for the default ``DB_ENGINE``, but can be optional for some engines.

See ``DATABASES.PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#port>`__.



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

The log level DSMR-reader should use. Choose either ``ERROR`` (omit for this default), ``WARNING`` or ``DEBUG`` (should be temporary due to file I/O).

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

See ``DATABASES.CONN_MAX_AGE`` in `Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#conn-max-age>`__. Omit to use the default.


``TZ``
~~~~~~
**Optional**

The timezone `Django should use <https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-TIME_ZONE>`__. Alter at your own risk. Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands).


``DJANGO_STATIC_URL``
~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``STATIC_URL`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#static-url>`__. Omit to use the default.


``DJANGO_FORCE_SCRIPT_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``FORCE_SCRIPT_NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#force-script-name>`__. Omit to use the default.


``DJANGO_USE_X_FORWARDED_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``USE_X_FORWARDED_HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-host>`__. Omit to use the default.


``DJANGO_USE_X_FORWARDED_PORT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``USE_X_FORWARDED_PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-port>`__. Omit to use the default.


``DJANGO_X_FRAME_OPTIONS``
~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``X_FRAME_OPTIONS`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#x-frame-options>`__. Omit to use the default.
