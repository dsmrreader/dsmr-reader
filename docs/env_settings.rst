Env Settings
============

You can either specify the following settings as system environments variables or define them in a ``.env`` file in the root of the DSMR-reader project folder.


.. attention::

    The following settings have been **renamed** since DSMR-reader ``v4.5``. Their old name will be **removed** in DSMR-reader ``v5.0``

    +-----------------------+--------------------------------------+
    | Old name < v4.5       | New name >= v4.5                     |
    +=======================+======================================+
    | ``SECRET_KEY``        | ``DJANGO_SECRET_KEY``                |
    +-----------------------+--------------------------------------+
    | ``DB_ENGINE``         | ``DJANGO_DATABASE_ENGINE``           |
    +-----------------------+--------------------------------------+
    | ``DB_HOST``           | ``DJANGO_DATABASE_HOST``             |
    +-----------------------+--------------------------------------+
    | ``DB_PORT``           | ``DJANGO_DATABASE_PORT``             |
    +-----------------------+--------------------------------------+
    | ``DB_NAME``           | ``DJANGO_DATABASE_NAME``             |
    +-----------------------+--------------------------------------+
    | ``DB_USER``           | ``DJANGO_DATABASE_USER``             |
    +-----------------------+--------------------------------------+
    | ``DB_PASS``           | ``DJANGO_DATABASE_PASSWORD``         |
    +-----------------------+--------------------------------------+
    | ``CONN_MAX_AGE``      | ``DJANGO_DATABASE_CONN_MAX_AGE``     |
    +-----------------------+--------------------------------------+
    | ``TZ``                | ``DJANGO_TIME_ZONE``                 |
    +-----------------------+--------------------------------------+
    | ``DSMR_USER``         | ``DSMRREADER_ADMIN_USER``            |
    +-----------------------+--------------------------------------+
    | ``DSMR_PASSWORD``     | ``DSMRREADER_ADMIN_PASSWORD``        |
    +-----------------------+--------------------------------------+


.. contents::


Django settings/overrides
-------------------------

DSMR-reader utilizes the Python Django framework.
All settings below directly affect or override Django, and therefor your DSMR-reader installation as well.

``DJANGO_SECRET_KEY`` (``SECRET_KEY``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::

    **Required setting**

The secret key Django should use. This should be randomly generated for your installation.
Generate or refresh it by running ``./tools/generate-secret-key.sh``.

.. seealso::

    See ``SECRET_KEY`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#secret-key>`__.

.. versionadded:: v4.5


----


``DJANGO_DATABASE_ENGINE`` (``DB_ENGINE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::

    **Required setting**

The database engine to use. Officially DSMR-reader only supports ``django.db.backends.postgresql``, but others supported by Django may work as well.
Experiment at your own risk!


.. seealso::

    See ``DATABASES.ENGINE`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#engine>`__.

.. versionadded:: v4.5


----


``DJANGO_DATABASE_HOST`` (``DB_HOST``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::

    **Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.


.. seealso::

    See ``DATABASES.HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#host>`__.

.. versionadded:: v4.5


----


``DJANGO_DATABASE_PORT`` (``DB_PORT``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::

    **Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.


.. seealso::

    See ``DATABASES.PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#port>`__.

.. versionadded:: v4.5


----


``DJANGO_DATABASE_NAME`` (``DB_NAME``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::

    **Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.


.. seealso::

    See ``DATABASES.NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#name>`__.

.. versionadded:: v4.5


----


``DJANGO_DATABASE_USER`` (``DB_USER``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::

    **Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.


.. seealso::

    See ``DATABASES.USER`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#user>`__.

.. versionadded:: v4.5


----


``DJANGO_DATABASE_PASSWORD`` (``DB_PASS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::

    **Required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.


.. seealso::

    See ``DATABASES.PASSWORD`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#password>`__.

.. versionadded:: v4.5


----


``DJANGO_DATABASE_CONN_MAX_AGE`` (``CONN_MAX_AGE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Optional setting**


.. seealso::

    See ``DATABASES.CONN_MAX_AGE`` in `Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#conn-max-age>`__. Omit to use the default.

.. versionadded:: v4.5


----


``DJANGO_TIME_ZONE`` (``TZ``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Optional setting**


.. seealso::

    The timezone `Django should use <https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-TIME_ZONE>`__. Alter at your own risk. Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands).

.. versionadded:: v4.5


----


``DJANGO_STATIC_URL``
~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**



.. seealso::

    See ``STATIC_URL`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#static-url>`__. Omit to use the default.

.. versionadded:: v4.5


----


``DJANGO_FORCE_SCRIPT_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**


.. seealso::

    See ``FORCE_SCRIPT_NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#force-script-name>`__. Omit to use the default.

.. versionadded:: v4.5


----


``DJANGO_USE_X_FORWARDED_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**


.. seealso::

    See ``USE_X_FORWARDED_HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-host>`__. Omit to use the default.

.. versionadded:: v4.5


----


``DJANGO_USE_X_FORWARDED_PORT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**


.. seealso::

    See ``USE_X_FORWARDED_PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-port>`__. Omit to use the default.

.. versionadded:: v4.5


----


``DJANGO_X_FRAME_OPTIONS``
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**


.. seealso::

    See ``X_FRAME_OPTIONS`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#x-frame-options>`__. Omit to use the default.

.. versionadded:: v4.5


----


``DJANGO_STATIC_ROOT``
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**


.. seealso::

    See ``STATIC_ROOT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#static-root>`__. Omit to use the default.

.. versionadded:: v4.6


----


DSMR-reader settings
--------------------

``DSMRREADER_ADMIN_USER`` (``DSMR_USER``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**

The username of the **webinterface** (super)user to create when running ``./manage.py dsmr_superuser``.

.. versionadded:: v4.5


----


``DSMRREADER_ADMIN_PASSWORD`` (``DSMR_PASSWORD``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Situational setting**

The password of the ``DSMR_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.

.. versionadded:: v4.5


----


``DSMRREADER_LOGLEVEL``
~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Optional setting**

The log level DSMR-reader should use. Choose either ``ERROR`` (omit for this default), ``WARNING`` or ``DEBUG`` (should be temporary due to file I/O).


.. seealso::

    For more information, :doc:`see Troubleshooting<troubleshooting>`.

.. versionadded:: v4.5


----


``DSMRREADER_PLUGINS``
~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Optional setting**

The plugins DSMR-reader should use. Omit to use the default of no plugins.
Note that this should be a comma separated list when specifying multiple plugins. E.g.::

    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1
    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1,dsmr_plugins.modules.plugin_name2


.. seealso::

    For more information, :doc:`see Plugins<plugins>`.

.. versionadded:: v4.5


----


``DSMRREADER_SUPPRESS_STORAGE_SIZE_WARNINGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Optional setting**

Whether to suppress any warnings regarding too many readings stored or the database size.
Set it to ``True`` to disable the warnings or omit it to use the default (``False``).
Suppress at your own risk.

.. versionadded:: v4.6
