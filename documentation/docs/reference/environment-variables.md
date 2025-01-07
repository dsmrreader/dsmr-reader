# Environment variables

[TOC]

**Django settings/overrides**

DSMR-reader utilizes the Python Django framework. All settings below directly affect or override Django.


## ``DJANGO_SECRET_KEY``

!!! failure inline end ""

    This setting is **required**.

The secret key Django should use for some security internals. Should be unique and kept a secret. Generate a random value

See [``SECRET_KEY`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key) for more information about the setting and what it does.

---

## ``DJANGO_DATABASE_ENGINE``

!!! failure inline end ""

    This setting is **required**.

The database engine to use. 

DSMR-reader is developed and tested with PostgreSQL, but other engines supported by Django may work as well. E.g. MySQL.

See [``DATABASES.ENGINE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#engine) for more information about the setting and what it does.

!!! danger
    
    Use engines, other than ``django.db.backends.postgresql``, at your own risk!

---

## ``DJANGO_DATABASE_HOST``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the host name to connect to.

See [``DATABASES.HOST`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#host) for more information about the setting and what it does.

---

## ``DJANGO_DATABASE_PORT``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the host port to connect to.

See [``DATABASES.PORT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#port) for more information about the setting and what it does.

---

## ``DJANGO_DATABASE_NAME``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the database name to connect to.

See [``DATABASES.NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#name) for more information about the setting and what it does.

---

## ``DJANGO_DATABASE_USER``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the database username to connect with.

See [``DATABASES.USER`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#user) for more information about the setting and what it does.

---

## ``DJANGO_DATABASE_PASSWORD``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the database password to connect with.

See [``DATABASES.PASSWORD`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#password) for more information about the setting and what it does.

---

## ``DJANGO_DATABASE_CONN_MAX_AGE``

!!! info inline end ""

    This setting is **optional**.

Database connection setting. For the default engine is not needed.

See [``DATABASES.CONN_MAX_AGE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#conn-max-age) for more information about the setting and what it does.

---

## ``DJANGO_TIME_ZONE``

!!! info inline end ""

    This setting is **optional**.

The timezone Django should use. Alter at your own risk. 

Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands and other countries in the same timezone).

See [``TIME_ZONE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-TIME_ZONE) for more information about the setting and what it does.

---

## ``DJANGO_ALLOWED_HOSTS``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Setting related to incoming Host headers. Only applicable if you expose your DSMR-reader installation directly to the public Internet.

See [``ALLOWED_HOSTS`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts) for more information about the setting and what it does.

!!! tip

    If you have **multiple hosts** to allow, pass them as a **comma separated** value. E.g.:

    ```ini
    DJANGO_ALLOWED_HOSTS=https://subdomain1.example.com,https://subdomain2.example.com,https://subdomain3.example.com
    ```

---

## ``DJANGO_STATIC_URL``

!!! example inline end ""

    This setting is **situational**.

See [``STATIC_URL`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#static-url) for more information about the setting and what it does.

---

## ``DJANGO_FORCE_SCRIPT_NAME``

!!! example inline end ""

    This setting is **situational**.

See [``FORCE_SCRIPT_NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#force-script-name) for more information about the setting and what it does.

---

## ``DJANGO_USE_X_FORWARDED_HOST``

!!! example inline end ""

    This setting is **situational**.

See [``USE_X_FORWARDED_HOST`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#use-x-forwarded-host) for more information about the setting and what it does.

---

## ``DJANGO_USE_X_FORWARDED_PORT``

!!! example inline end ""

    This setting is **situational**.

See [``USE_X_FORWARDED_PORT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#use-x-forwarded-port) for more information about the setting and what it does.

---

## ``DJANGO_X_FRAME_OPTIONS``

!!! example inline end ""

    This setting is **situational**.

See [``X_FRAME_OPTIONS`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#x-frame-options) for more information about the setting and what it does.

---

## ``DJANGO_STATIC_ROOT``

!!! example inline end ""

    This setting is **situational**.

See [``STATIC_ROOT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#static-root) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_AGE``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_AGE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-age) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_DOMAIN``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_DOMAIN`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-domain) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_HTTPONLY``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_HTTPONLY`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-httponly) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_MASKED``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_MASKED`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-masked) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_NAME``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-name) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_PATH``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_PATH`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-path) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_SAMESITE``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_SAMESITE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-samesite) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_COOKIE_SECURE``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_SECURE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-secure) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_USE_SESSIONS``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_USE_SESSIONS`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-use-sessions) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_HEADER_NAME``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_HEADER_NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-header-name) for more information about the setting and what it does.

---

## ``DJANGO_CSRF_TRUSTED_ORIGINS``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_TRUSTED_ORIGINS`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins) for more information about the setting and what it does.

!!! tip

    If you have **multiple domains** to trust, pass them as a **comma separated** value. E.g.:

    ```ini
    DJANGO_CSRF_TRUSTED_ORIGINS=https://subdomain1.example.com,https://subdomain2.example.com,https://subdomain3.example.com
    ```

---

---

---

**DSMR-reader settings**

These settings are for this project only.

## ``DSMRREADER_ADMIN_USER``

!!! example inline end ""

    This setting is **situational**.

The username of the **webinterface** (super)user to create when running ``./manage.py dsmr_superuser``.

---

## ``DSMRREADER_ADMIN_PASSWORD``

!!! example inline end ""

    This setting is **situational**.

The password of the ``DSMRREADER_ADMIN_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.

---


## ``DSMRREADER_LOGLEVEL``

!!! example inline end ""

    This setting is **situational**.

The log level DSMR-reader should use. Choose either:

- ``ERROR`` (omit for this default)
- ``WARNING``
- ``DEBUG``
 
The latter should only be used for debugging DSMR-reader and pinpointing weird issues.

---

## ``DSMRREADER_PLUGINS``

!!! example ""

    This setting is **situational**.

The [plugins DSMR-reader should use](./plugins.md). Omit to use the default of no plugins.
Note that this should be a comma separated list when specifying multiple plugins. E.g.:

```ini
DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1
DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1,dsmr_plugins.modules.plugin_name2
```

---

## ``DSMRREADER_SUPPRESS_STORAGE_SIZE_WARNINGS``

!!! example ""

    This setting is **situational**.

Whether to suppress any warnings regarding too many readings stored or the database size.
Set it to ``True`` to **disable the warnings** or omit it to use the default (= ``False``).

!!! danger

    Suppress warnings at your own risk.

---

## ``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE``

!!! example ""

    This setting is **situational**.

The maximum amount of MQTT messages queued in DSMR-reader until new ones will be **rejected**. No need to tweak this for healthy installations.

This prevents creating an infinite backlog of messages queued. 
For example when the pile of unsent messages keeps increasing and DSMR-reader is unable to send them faster than new ones are created.

However, you may increase the maximum for whatever reason along your local setup.
Omit to use the default (a few thousand).

!!! danger

    Increase queue size at your own risk.

---

## ``DSMRREADER_MQTT_MAX_CACHE_TIMEOUT``

!!! example ""

    This setting is **situational**.

Updating MQTT topics consecutively **with the same value has no effect**, depending on its usage in your setup.

DSMR-reader always sends MQTT messages to your broker with a ``retain`` flag, resulting the broker keeping the **last value received for every topic**. 
Which means that any (new) MQTT subscribers should always receive the retained value, even when DSMR-reader has no *new* (different) values for the retained topics. 

To take advantage of this, DSMR-reader can be set to *cache the last value sent for each topic*. This will hint DSMR-reader to **not send the same consecutive value to the same topic** (within the caching duration).
This may greatly reduce the number of MQTT messages sent when there is nothing to update, as DSMR-reader will simply not send an update. 

If the value of a topic changes, DSMR-reader will still send the updated value. Data that *constantly changes* will not be affected by this mechanism (and the entire mechanism will be useless for those topics).

!!! danger

    Enable caching only if you understand what it does.
