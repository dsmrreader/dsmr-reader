# Environment variables

[TOC]

**Django settings/overrides**

DSMR-reader utilizes the Python Django framework. All settings below directly affect or override Django.


## ``DJANGO_SECRET_KEY``

!!! failure inline end ""

    This setting is **required**.

The secret key Django should use for some security internals. Should be unique and kept a secret. Generate a random value

See [``SECRET_KEY`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key) for more information about the setting and what it does.

----

## ``DJANGO_DATABASE_ENGINE``

!!! failure inline end ""

    This setting is **required**.

The database engine to use. Officially DSMR-reader only supports PostgreSQL, but others supported by Django may work as well.

See [``DATABASES.ENGINE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#engine) for more information about the setting and what it does.

!!! danger
    
    Use engines other than ``django.db.backends.postgresql`` at your own risk!

----

## ``DJANGO_DATABASE_HOST``

!!! failure inline end ""

    This setting is **required**. But also depends on the engine used (and may be optional in some situations).

Database connection setting. For the default engine it's the host name to connect to.

See [``DATABASES.HOST`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#host) for more information about the setting and what it does.

----

## ``DJANGO_DATABASE_PORT``

!!! failure inline end ""

    This setting is **required**. But also depends on the engine used (and may be optional in some situations).

Database connection setting. For the default engine it's the host port to connect to.

See [``DATABASES.PORT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#port) for more information about the setting and what it does.

----

## ``DJANGO_DATABASE_NAME``

!!! failure inline end ""

    This setting is **required**. But also depends on the engine used (and may be optional in some situations).

Database connection setting. For the default engine it's the database name to connect to.

See [``DATABASES.NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#name) for more information about the setting and what it does.

----

## ``DJANGO_DATABASE_USER``

!!! failure inline end ""

    This setting is **required**. But also depends on the engine used (and may be optional in some situations).

Database connection setting. For the default engine it's the database username to connect with.

See [``DATABASES.USER`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#user) for more information about the setting and what it does.

----

## ``DJANGO_DATABASE_PASSWORD``

!!! failure inline end ""

    This setting is **required**. But also depends on the engine used (and may be optional in some situations).

Database connection setting. For the default engine it's the database password to connect with.

See [``DATABASES.PASSWORD`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#password) for more information about the setting and what it does.

----

## ``DJANGO_DATABASE_CONN_MAX_AGE``

!!! info inline end ""

    This setting is **optional**.

Database connection setting. For the default engine is not needed.

See [``DATABASES.CONN_MAX_AGE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#conn-max-age) for more information about the setting and what it does.

----

## ``DJANGO_TIME_ZONE``

!!! info inline end ""

    This setting is **optional**.

The timezone Django should use. Alter at your own risk. Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands).

See [``TIME_ZONE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-TIME_ZONE) for more information about the setting and what it does.


----


## ``DJANGO_STATIC_URL``

!!! example inline end ""

    This setting is **situational**.

See [``STATIC_URL`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#static-url) for more information about the setting and what it does.

----


## ``DJANGO_FORCE_SCRIPT_NAME``

!!! example inline end ""

    This setting is **situational**.

See [``FORCE_SCRIPT_NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#force-script-name) for more information about the setting and what it does.

----

## ``DJANGO_USE_X_FORWARDED_HOST``

!!! example inline end ""

    This setting is **situational**.

See [``USE_X_FORWARDED_HOST`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#use-x-forwarded-host) for more information about the setting and what it does.

----

## ``DJANGO_USE_X_FORWARDED_PORT``

!!! example inline end ""

    This setting is **situational**.

See [``USE_X_FORWARDED_PORT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#use-x-forwarded-port) for more information about the setting and what it does.

----

## ``DJANGO_X_FRAME_OPTIONS``

!!! example inline end ""

    This setting is **situational**.

See [``X_FRAME_OPTIONS`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#x-frame-options) for more information about the setting and what it does.

----

## ``DJANGO_STATIC_ROOT``

!!! example inline end ""

    This setting is **situational**.

See [``STATIC_ROOT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#static-root) for more information about the setting and what it does.

----


**DSMR-reader settings**

These settings are for this project only.

## ``DSMRREADER_ADMIN_USER``

!!! example inline end ""

    This setting is **situational**.

The username of the **webinterface** (super)user to create when running ``./manage.py dsmr_superuser``.

----

## ``DSMRREADER_ADMIN_PASSWORD``

!!! example inline end ""

    This setting is **situational**.

The password of the ``DSMRREADER_ADMIN_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.

----


## ``DSMRREADER_LOGLEVEL``

!!! example inline end ""

    This setting is **situational**.

The log level DSMR-reader should use. Choose either:

- ``ERROR`` (omit for this default)
- ``WARNING``
- ``DEBUG``
 
The latter should only be used for debugging DSMR-reader and pinpointing weird issues.

----

## ``DSMRREADER_PLUGINS``

!!! example inline end ""

    This setting is **situational**.

The [plugins DSMR-reader should use](./plugins.md). Omit to use the default of no plugins.
Note that this should be a comma separated list when specifying multiple plugins. E.g.:

```ini
DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1
DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1,dsmr_plugins.modules.plugin_name2
```

----

## ``DSMRREADER_SUPPRESS_STORAGE_SIZE_WARNINGS``

!!! example inline end ""

    This setting is **situational**.

Whether to suppress any warnings regarding too many readings stored or the database size.
Set it to ``True`` to **disable the warnings** or omit it to use the default (= ``False``).

!!! danger

    Suppress warnings at your own risk.

----

## ``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE``

!!! example inline end ""

    This setting is **situational**.

The maximum amount of MQTT messages queued in DSMR-reader until new ones will be **rejected**. No need to tweak this for healthy installations.

This prevents creating an infinite backlog of messages queued. 
For example when the pile of unsent messages keeps increasing and DSMR-reader is unable to send them faster than new ones are created.

However, you may increase the maximum for whatever reason along your local setup.
Omit to use the default (a few thousand).

!!! danger

    Increase queue size at your own risk.

----

## ``DSMRREADER_MQTT_MAX_CACHE_TIMEOUT``

!!! example inline end ""

    This setting is **situational**.

Updating MQTT topics consecutively **with the same value has no effect**, depending on its usage in your setup.

DSMR-reader sends MQTT messages to your broker with a ``retain`` flag, resulting the broker keeping the last value received for every topic. 
Which means that any MQTT subscribers should always receive the retained value, even when DSMR-reader has no updates. 

DSMR-reader can be set to *cache the last value sent for each topic*. It will cause DSMR-reader to **not send the same value to the same topic consecutively** (within the caching duration).
This may greatly reduce the number of MQTT messages sent when there is nothing to update. If the value of a topic changes, DSMR-reader will still send the updated value.

!!! danger

    Enable caching only if you understand what it does.
