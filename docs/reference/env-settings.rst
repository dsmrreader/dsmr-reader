Environment settings
====================

.. contents::
    :depth: 2


.. contents::
    :depth: 2


Django settings/overrides
-------------------------

DSMR-reader utilizes the Python Django framework.
All settings below directly affect or override Django, and therefor your DSMR-reader installation as well.


.. tip::

    You can either specify the following settings:

    - in a ``.env`` file in the root of the DSMR-reader project folder (manual installations)
    - or as system environments variables (Docker installations)


.. contents:: :local:
    :depth: 1


``DJANGO_SECRET_KEY``
~~~~~~~~~~~~~~~~~~~~~

The secret key Django should use. This should be randomly generated for your installation.
Generate or refresh it by running ``./tools/generate-secret-key.sh``.

.. seealso::

    See ``SECRET_KEY`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#secret-key>`__.

.. hint::

    **This setting is required**

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``SECRET_KEY`` env var.

----


``DJANGO_DATABASE_ENGINE``
~~~~~~~~~~~~~~~~~~~~~~~~~~

The database engine to use. Officially DSMR-reader only supports ``django.db.backends.postgresql``, but others supported by Django may work as well.
Experiment at your own risk!

.. seealso::

    See ``DATABASES.ENGINE`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#engine>`__.

.. hint::

    **This setting is required**

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DB_ENGINE`` env var.


----


``DJANGO_DATABASE_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``DATABASES.HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#host>`__.

.. hint::

    **This setting is required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DB_HOST`` env var.


----


``DJANGO_DATABASE_PORT``
~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``DATABASES.PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#port>`__.

.. hint::

    **This setting is required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DB_PORT`` env var.


----


``DJANGO_DATABASE_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``DATABASES.NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#name>`__.

.. hint::

    **This setting is required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DB_NAME`` env var.


----


``DJANGO_DATABASE_USER``
~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``DATABASES.USER`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#user>`__.

.. hint::

    **This setting is required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DB_USER`` env var.


----


``DJANGO_DATABASE_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``DATABASES.PASSWORD`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#password>`__.

.. hint::

    **This setting is required** for the default ``DJANGO_DATABASE_ENGINE``, but can be optional for some engines.

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DB_PASS`` env var.


----


``DJANGO_DATABASE_CONN_MAX_AGE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``DATABASES.CONN_MAX_AGE`` in `Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#conn-max-age>`__. Omit to use the default.

.. hint::

    **This setting is optional**

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``CONN_MAX_AGE`` env var.


----


``DJANGO_TIME_ZONE``
~~~~~~~~~~~~~~~~~~~~

The timezone Django should use. Alter at your own risk. Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands).

.. seealso::

    See ``TIME_ZONE`` in `Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-TIME_ZONE>`__.

.. hint::

    **This setting is optional**

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``TZ`` env var.


----


``DJANGO_STATIC_URL``
~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``STATIC_URL`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#static-url>`__. Omit to use the default.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.5


----


``DJANGO_FORCE_SCRIPT_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``FORCE_SCRIPT_NAME`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#force-script-name>`__. Omit to use the default.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.5


----


``DJANGO_USE_X_FORWARDED_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``USE_X_FORWARDED_HOST`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-host>`__. Omit to use the default.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.5


----


``DJANGO_USE_X_FORWARDED_PORT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    See ``USE_X_FORWARDED_PORT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#use-x-forwarded-port>`__. Omit to use the default.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.5


----


``DJANGO_X_FRAME_OPTIONS``
~~~~~~~~~~~~~~~~~~~~~~~~~~


.. seealso::

    See ``X_FRAME_OPTIONS`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#x-frame-options>`__. Omit to use the default.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.5


----


``DJANGO_STATIC_ROOT``
~~~~~~~~~~~~~~~~~~~~~~~~~~


.. seealso::

    See ``STATIC_ROOT`` `in Django docs <https://docs.djangoproject.com/en/3.1/ref/settings/#static-root>`__. Omit to use the default.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.6


----


DSMR-reader settings
--------------------

These settings are for DSMR-reader only.


.. tip::

    You can either specify the following settings:

    - in a ``.env`` file in the root of the DSMR-reader project folder (manual installations)
    - or as system environments variables (Docker installations)


.. contents:: :local:
    :depth: 1


``DSMRREADER_ADMIN_USER``
~~~~~~~~~~~~~~~~~~~~~~~~~

The username of the **webinterface** (super)user to create when running ``./manage.py dsmr_superuser``.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DSMR_USER`` env var.


----


``DSMRREADER_ADMIN_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The password of the ``DSMRREADER_ADMIN_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.

.. hint::

    **This setting is situational**

    .. versionadded:: v4.5

    .. deprecated:: 4.5

        Former ``DSMR_PASSWORD`` env var.

----


``DSMRREADER_LOGLEVEL``
~~~~~~~~~~~~~~~~~~~~~~~

The log level DSMR-reader should use. Choose either ``ERROR`` (omit for this default), ``WARNING`` or ``DEBUG`` (should be temporary due to file I/O).

.. seealso::

    For more information, :doc:`see Troubleshooting</how-to/troubleshooting/enabling-debug-logging>`.

.. hint::

    **This setting is optional**

    .. versionadded:: v4.5


----


``DSMRREADER_PLUGINS``
~~~~~~~~~~~~~~~~~~~~~~~

The plugins DSMR-reader should use. Omit to use the default of no plugins.
Note that this should be a comma separated list when specifying multiple plugins. E.g.::

    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1
    DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1,dsmr_plugins.modules.plugin_name2


.. seealso::

    For more information, :doc:`see Plugins</reference/plugins>`.

.. hint::

    **This setting is optional**

    .. versionadded:: v4.5


----


``DSMRREADER_SUPPRESS_STORAGE_SIZE_WARNINGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whether to suppress any warnings regarding too many readings stored or the database size.
Set it to ``True`` to disable the warnings or omit it to use the default (``False``).
Suppress at your own risk.

.. hint::

    **This setting is optional**

    .. versionadded:: v4.6


----


``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The maximum amount of MQTT messages queued in DSMR-reader until new ones will be rejected.
This prevents creating an infinite backlog of messages queued.

However, situationally you may increase the maximum for whatever reason along your local setup.
Omit to use the default.

.. hint::

    **This setting is optional**

    .. versionadded:: v4.16


----


``DSMRREADER_MQTT_MAX_CACHE_TIMEOUT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MQTT messages sent by DSMR-reader to your broker with a ``retain`` flag, meaning that the broker will remember the last value received for those topics.
Updating retained MQTT topics consecutively with the same value has no effect. Therefor DSMR-reader caches the last value sent for each topic.
DSMR-reader will not queue nor send MQTT messages that exactly match the previous one, greatly reducing the number of MQTT messages sent.

However, situationally you may want to decrease cache duration or disable it entirely. Set to ``0`` to disable. Omit to use the default.

.. hint::

    **This setting is optional**

    .. versionadded:: v4.16
