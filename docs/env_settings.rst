Env Settings
============

.. contents::
    :depth: 2


You can either specify the following settings as system environments variables or define them in a ``.env`` file in the root of the DSMR-reader project folder.

.. attention::

    The following settings have been **renamed** since DSMR-reader ``v4.5``, but are still available.
    Their old name will be **removed** in DSMR-reader ``v5.0`` and can then be no longer used.

    +-----------------------+--------------------------------------+
    | Former name < v5.0    | New name >= v4.5                     |
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



Django settings/overrides
-------------------------

DSMR-reader utilizes the Python Django framework.
All settings below directly affect or override Django, and therefor your DSMR-reader installation as well.

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

The password of the ``DSMR_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.

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

    For more information, :doc:`see Troubleshooting in FAQ<faq>`.

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

    For more information, :doc:`see Plugins<plugins>`.

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
