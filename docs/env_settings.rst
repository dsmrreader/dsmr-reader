Env Settings
============

You can either specify the following settings as system environments variables or define them in a ``.env`` file in the root of the DSMR-reader project folder.


.. warning::

    The following settings have been **renamed** since DSMR-reader ``v4.5``. Their old name will be **removed** in DSMR-reader ``v5.0``::

        Name before v4.5    ->      New name since v4.5
        -----------------------------------------------
        SECRET_KEY          ->      DJANGO_SECRET_KEY
        DB_ENGINE           ->      DJANGO_DATABASE_ENGINE
        DB_HOST             ->      DJANGO_DATABASE_HOST
        DB_PORT             ->      DJANGO_DATABASE_PORT
        DB_NAME             ->      DJANGO_DATABASE_NAME
        DB_USER             ->      DJANGO_DATABASE_USER
        DB_PASS             ->      DJANGO_DATABASE_PASSWORD
        CONN_MAX_AGE        ->      DJANGO_DATABASE_CONN_MAX_AGE
        TZ                  ->      DJANGO_TIME_ZONE
        DSMR_USER           ->      DSMRREADER_ADMIN_USER
        DSMR_PASSWORD       ->      DSMRREADER_ADMIN_PASSWORD

.. contents::


Django settings/overrides
-------------------------

``SECRET_KEY`` / ``DJANGO_SECRET_KEY``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_SECRET_KEY`` since DSMR-reader ``v4.5`` and the old name ``SECRET_KEY`` will be removed in DSMR-reader ``v5.0``.

**Required**

The secret key Django should use. This should be randomly generated for your installation.
Generate or refresh it by running ``./tools/generate-secret-key.sh``.

See ``SECRET_KEY`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#secret-key>`__.

----

``DB_ENGINE`` / ``DJANGO_DATABASE_ENGINE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_DATABASE_ENGINE`` since DSMR-reader ``v4.5`` and the old name ``DB_ENGINE`` will be removed in DSMR-reader ``v5.0``.

**Required**

The database engine to use. Officially DSMR-reader only supports ``django.db.backends.postgresql``, but others supported by Django may work as well.
Experiment at your own risk!

See ``DATABASES.ENGINE`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#engine>`__.

----

``DB_HOST`` / ``DJANGO_DATABASE_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_DATABASE_HOST`` since DSMR-reader ``v4.5`` and the old name ``DB_HOST`` will be removed in DSMR-reader ``v5.0``.

**Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

See ``DATABASES.HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#host>`__.

----

``DB_PORT`` / ``DJANGO_DATABASE_PORT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_DATABASE_PORT`` since DSMR-reader ``v4.5`` and the old name ``DB_PORT`` will be removed in DSMR-reader ``v5.0``.

**Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

See ``DATABASES.PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#port>`__.

----

``DB_NAME`` / ``DJANGO_DATABASE_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_DATABASE_NAME`` since DSMR-reader ``v4.5`` and the old name ``DB_NAME`` will be removed in DSMR-reader ``v5.0``.

**Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

See ``DATABASES.NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#name>`__.

----

``DB_USER`` / ``DJANGO_DATABASE_USER``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_DATABASE_USER`` since DSMR-reader ``v4.5`` and the old name ``DB_USER`` will be removed in DSMR-reader ``v5.0``.

**Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

See ``DATABASES.USER`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#user>`__.

----

``DB_PASS`` / ``DJANGO_DATABASE_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_DATABASE_PASSWORD`` since DSMR-reader ``v4.5`` and the old name ``DB_PASS`` will be removed in DSMR-reader ``v5.0``.

**Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

See ``DATABASES.PASSWORD`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#password>`__.

----

``CONN_MAX_AGE`` / ``DJANGO_DATABASE_CONN_MAX_AGE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_DATABASE_CONN_MAX_AGE`` since DSMR-reader ``v4.5`` and the old name ``CONN_MAX_AGE`` will be removed in DSMR-reader ``v5.0``.

**Optional**

See ``DATABASES.CONN_MAX_AGE`` in `Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#conn-max-age>`__. Omit to use the default.

----

``TZ`` / ``DJANGO_TIME_ZONE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DJANGO_TIME_ZONE`` since DSMR-reader ``v4.5`` and the old name ``TZ`` will be removed in DSMR-reader ``v5.0``.

**Optional**

The timezone `Django should use <https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-TIME_ZONE>`__. Alter at your own risk. Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands).

----

``DJANGO_STATIC_URL``
~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``STATIC_URL`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#static-url>`__. Omit to use the default.

----

``DJANGO_FORCE_SCRIPT_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``FORCE_SCRIPT_NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#force-script-name>`__. Omit to use the default.

----

``DJANGO_USE_X_FORWARDED_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``USE_X_FORWARDED_HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-host>`__. Omit to use the default.

----

``DJANGO_USE_X_FORWARDED_PORT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``USE_X_FORWARDED_PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-port>`__. Omit to use the default.

----

``DJANGO_X_FRAME_OPTIONS``
~~~~~~~~~~~~~~~~~~~~~~~~~~
**Situational**

See ``X_FRAME_OPTIONS`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#x-frame-options>`__. Omit to use the default.

----

DSMR-reader settings
--------------------

``DSMR_USER`` / ``DSMRREADER_ADMIN_USER``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DSMRREADER_ADMIN_USER`` since DSMR-reader ``v4.5`` and the old name ``DSMR_USER`` will be removed in DSMR-reader ``v5.0``.

**Situational**

The username of the **webinterface** (super)user to create when running ``./manage.py dsmr_superuser``.

----

``DSMR_PASSWORD`` / ``DSMRREADER_ADMIN_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Renamed to ``DSMRREADER_ADMIN_PASSWORD`` since DSMR-reader ``v4.5`` and the old name ``DSMR_PASSWORD`` will be removed in DSMR-reader ``v5.0``.

**Situational**

The password of the ``DSMR_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.

----

``DSMRREADER_LOGLEVEL``
~~~~~~~~~~~~~~~~~~~~~~~
**Optional**

The log level DSMR-reader should use. Choose either ``ERROR`` (omit for this default), ``WARNING`` or ``DEBUG`` (should be temporary due to file I/O).

For more information, :doc:`see Troubleshooting<troubleshooting>`.

----

``DSMRREADER_PLUGINS``
~~~~~~~~~~~~~~~~~~~~~~~
**Optional**

The plugins DSMR-reader should use. Omit to use the default of no plugins.
Note that this should be a comma separated list when specifying multiple plugins. E.g.::

    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1
    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1,dsmr_plugins.modules.plugin_name2

For more information, :doc:`see Plugins<plugins>`.

----

``DSMRREADER_SUPPRESS_STORAGE_SIZE_WARNINGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Optional**

Whether to suppress any warnings regarding too many readings stored or the database size.
Set it to ``True`` to disable the warnings or omit it to use the default (``False``).
Suppress at your own risk. Added in DSMR-reader ``v4.6``.
