# Environment variables

!!! note ""

    These environment variables can be used to configure DSMR-reader and its underlying Django framework.

    Apply them by defining them in your ``compose.env`` and restart the DSMR-reader container (e.g. ``podman-compose up -d``).


## DSMR-reader settings

These settings are for this main project only. Others may or may not exist or are specifically created for the DSMR-reader Docker project.

### ``DSMRREADER_ADMIN_USER``

!!! example inline end ""

    This setting is **situational**.

The username of the **webinterface** (super)user to create when running ``./manage.py dsmr_superuser``.

---

### ``DSMRREADER_ADMIN_PASSWORD``

!!! example inline end ""

    This setting is **situational**.

The password of the ``DSMRREADER_ADMIN_USER`` user to create (or update if the user exists) when running ``./manage.py dsmr_superuser``.

---

### ``DSMRREADER_LOGLEVEL``

!!! example inline end ""

    This setting is **situational**.

The log level DSMR-reader should use. Choose either:

- ``ERROR`` (omit for this default)
- ``WARNING``
- ``DEBUG``
 
The latter should only be used for debugging DSMR-reader and pinpointing weird issues.

---

### ``DSMRREADER_PLUGINS``

!!! example ""

    This setting is **situational**.

The [plugins DSMR-reader should use](./plugins.md). Omit to use the default of no plugins.
Note that this should be a comma separated list when specifying multiple plugins. E.g.:

```ini
DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1
```
```ini
DSMRREADER_PLUGINS=dsmr_plugins.modules.plugin_name1,dsmr_plugins.modules.plugin_name2
```

---

### ``DSMRREADER_SUPPRESS_STORAGE_SIZE_WARNINGS``

!!! example ""

    This setting is **situational**.

Whether to suppress any warnings regarding too many readings stored or the database size.
Set it to ``True`` to **disable the warnings** or omit it to use the default (= ``False``).

!!! danger

    Suppress warnings at your own risk.

---

### ``DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE``

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

### ``DSMRREADER_MQTT_MAX_CACHE_TIMEOUT``

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

---

### ``DSMRREADER_DECIMAL_SIZE_FORMATTING``

!!! question ""

    *This environment variable was added in DSMR-reader v6.1*

!!! note inline end ""

    This setting is **optional**.

Controls whether decimal values displayed in the web interface are rendered with the fractional part visually smaller than the integer part.

Set to ``False`` to display plain localized values. Omit to use the default (``True``).

```ini
DSMRREADER_DECIMAL_SIZE_FORMATTING=False
```

---

### ``DSMRREADER_BACKEND_HIBERNATE``

!!! example ""

    This setting is **situational** and should only be used **temporarily**.

Allows you to run DSMR-reader with the **backend process disabled**. 
This will stop all background tasks and allow you to run through the webinterface and datalogger without any background processing interfering.
You do not need this if you have no other installation running. Or when they are not interfering with each other.

This should only be a temporary state to test your database backup import. 
After testing, you should either wipe the entire installation and start fresh, or disable this setting when you are happy with the imported data and want to continue using the installation.
Don't forget to disable your previous installation if you go for the latter.

!!! example

    Example processes that *may interfere* with your other installation running:

    - Datalogger USB device
    - Dropbox backup upload
    - MQTT upload
    - InfluxDB upload
    - MinderGas upload
    - PVOutput upload

    Set to ``DSMRREADER_BACKEND_HIBERNATE=True`` to enable hibernation mode. Dropping this option will suffice to disable it again.

!!! danger

    Enable only if you understand what it does. Don't forget to disabled it later!

---

## DSMR-reader remote datalogger settings

These settings are specifically for the using the remote datalogger. You probably don't need these when using `ser2net` or a direct USB connection.

### ``DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD``

!!! failure inline end ""

    This setting is **required** for the remote datalogger script.

The input method the remote datalogger should use. Choose either:

- ``serial`` - For reading telegrams directly from a serial port
- ``ipv4`` - For reading telegrams from a network socket (e.g. ``ser2net``)

---

### ``DSMRREADER_REMOTE_DATALOGGER_API_HOSTS``

!!! failure inline end ""

    This setting is **required** for the remote datalogger script.

The DSMR-reader API host(s) to forward telegrams to. Include the schema (``http://`` or ``https://``) and port if needed.

For multiple hosts, use a comma separated list. E.g.:

```ini
DSMRREADER_REMOTE_DATALOGGER_API_HOSTS=http://12.34.56.78
```
```ini
DSMRREADER_REMOTE_DATALOGGER_API_HOSTS=http://12.34.56.78:7777,http://87.65.43.21:7777
```

---

### ``DSMRREADER_REMOTE_DATALOGGER_API_KEYS``

!!! failure inline end ""

    This setting is **required** for the remote datalogger script.

The DSMR-reader API key(s) corresponding to the host(s) specified in ``DSMRREADER_REMOTE_DATALOGGER_API_HOSTS``.

For multiple keys, use a comma separated list (in the same order as the hosts). E.g.:

```ini
DSMRREADER_REMOTE_DATALOGGER_API_KEYS=1234567890ABCDEFGH
```
```ini
DSMRREADER_REMOTE_DATALOGGER_API_KEYS=1234567890ABCDEFGH,0987654321HGFEDCBA
```

---

### ``DSMRREADER_REMOTE_DATALOGGER_SERIAL_PORT``

!!! warning inline end ""

    This setting is **required** when ``DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD=serial``.

The serial port to read telegrams from. E.g.:

```ini
DSMRREADER_REMOTE_DATALOGGER_SERIAL_PORT=/dev/ttyUSB0
```

---

### ``DSMRREADER_REMOTE_DATALOGGER_SERIAL_BAUDRATE``

!!! note inline end ""

    This setting is **optional** when ``DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD=serial``.

The baud rate for the serial port connection. Omit to use the default (``115200``).

- For DSMR v4/v5 meters: ``115200`` (default)
- For DSMR v2/v3 meters: ``9600``

---

### ``DSMRREADER_REMOTE_DATALOGGER_SERIAL_BYTESIZE``

!!! note inline end ""

    This setting is **optional** when ``DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD=serial``.

The byte size for the serial port connection. Omit to use the default (``8``).

- For DSMR v4/v5 meters: ``8`` (default)
- For DSMR v2/v3 meters: ``7``

---

### ``DSMRREADER_REMOTE_DATALOGGER_SERIAL_PARITY``

!!! note inline end ""

    This setting is **optional** when ``DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD=serial``.

The parity for the serial port connection. Omit to use the default (``N``).

- For DSMR v4/v5 meters: ``N`` (default)
- For DSMR v2/v3 meters: ``E``

---

### ``DSMRREADER_REMOTE_DATALOGGER_NETWORK_HOST``

!!! warning inline end ""

    This setting is **required** when ``DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD=ipv4``.

The hostname or IP address of the network socket to read telegrams from (e.g. when using ``ser2net``).

---

### ``DSMRREADER_REMOTE_DATALOGGER_NETWORK_PORT``

!!! warning inline end ""

    This setting is **required** when ``DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD=ipv4``.

The port of the network socket to read telegrams from.

---

### ``DSMRREADER_REMOTE_DATALOGGER_TIMEOUT``

!!! note inline end ""

    This setting is **optional**.

The timeout in seconds that applies to reading the serial port and/or writing to the DSMR-reader API. Omit to use the default (``20``).

---

### ``DSMRREADER_REMOTE_DATALOGGER_SLEEP``

!!! note inline end ""

    This setting is **optional**.

The time in seconds that the datalogger will pause after each telegram written to the DSMR-reader API. Omit to use the default (``0.5``).

---

### ``DSMRREADER_REMOTE_DATALOGGER_MIN_SLEEP_FOR_RECONNECT``

!!! note inline end ""

    This setting is **optional**.

The minimum sleep time in seconds before the datalogger will reconnect to the serial port or network socket. Omit to use the default (``1.0``).

---

### ``DSMRREADER_REMOTE_DATALOGGER_DEBUG_LOGGING``

!!! note inline end ""

    This setting is **optional**.

Set to ``True`` or ``1`` to enable verbose debug logging. Omit to disable.

!!! warning

    Enabling this logging for a long period of time on a Raspberry Pi may cause accelerated wearing of your SD card!

---

---

## Django settings/overrides

DSMR-reader utilizes the Python Django framework. All settings below directly affect or override Django.


### ``DJANGO_SECRET_KEY``

!!! failure inline end ""

    This setting is **required**.

The secret key Django should use for some security internals. Should be unique and kept a secret.
Find a password generator (e.g. [LastPass Password Generator](https://www.lastpass.com/features/password-generator), 50 characters, **no** symbols) and generate a new `DJANGO_SECRET_KEY`.

See [``SECRET_KEY`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key) for more information about the setting and what it does.

---

### ``DJANGO_DATABASE_ENGINE``

!!! failure inline end ""

    This setting is **required**.

The database engine to use. 

DSMR-reader is developed and tested with PostgreSQL, but other engines supported by Django may work as well. E.g. MySQL.

See [``DATABASES.ENGINE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#engine) for more information about the setting and what it does.

!!! danger
    
    Use engines, other than ``django.db.backends.postgresql``, at your own risk!

---

### ``DJANGO_DATABASE_HOST``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the host name to connect to.

See [``DATABASES.HOST`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#host) for more information about the setting and what it does.

---

### ``DJANGO_DATABASE_PORT``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the host port to connect to.

See [``DATABASES.PORT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#port) for more information about the setting and what it does.

---

### ``DJANGO_DATABASE_NAME``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the database name to connect to.

See [``DATABASES.NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#name) for more information about the setting and what it does.

---

### ``DJANGO_DATABASE_USER``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the database username to connect with.

See [``DATABASES.USER`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#user) for more information about the setting and what it does.

---

### ``DJANGO_DATABASE_PASSWORD``

!!! warning inline end ""

    This setting is **situationally required**, as it depends on the engine used.

Database connection setting. For the default engine it's the database password to connect with.

See [``DATABASES.PASSWORD`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#password) for more information about the setting and what it does.

---

### ``DJANGO_DATABASE_CONN_MAX_AGE``

!!! note inline end ""

    This setting is **optional**.

Database connection setting. For the default engine is not needed.

See [``DATABASES.CONN_MAX_AGE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#conn-max-age) for more information about the setting and what it does.

---

### ``DJANGO_TIME_ZONE``

!!! note inline end ""

    This setting is **optional**.

The timezone Django should use. Alter at your own risk. 

Omit to use the default, using the CET/CEST timezone (applicable to the Netherlands and other countries in the same timezone).

See [``TIME_ZONE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-TIME_ZONE) for more information about the setting and what it does.

---

### ``DJANGO_ALLOWED_HOSTS``

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

### ``DJANGO_STATIC_URL``

!!! example inline end ""

    This setting is **situational**.

See [``STATIC_URL`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#static-url) for more information about the setting and what it does.

---

### ``DJANGO_FORCE_SCRIPT_NAME``

!!! example inline end ""

    This setting is **situational**.

See [``FORCE_SCRIPT_NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#force-script-name) for more information about the setting and what it does.

---

### ``DJANGO_USE_X_FORWARDED_HOST``

!!! example inline end ""

    This setting is **situational**.

See [``USE_X_FORWARDED_HOST`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#use-x-forwarded-host) for more information about the setting and what it does.

---

### ``DJANGO_USE_X_FORWARDED_PORT``

!!! example inline end ""

    This setting is **situational**.

See [``USE_X_FORWARDED_PORT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#use-x-forwarded-port) for more information about the setting and what it does.

---

### ``DJANGO_X_FRAME_OPTIONS``

!!! example inline end ""

    This setting is **situational**.

See [``X_FRAME_OPTIONS`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#x-frame-options) for more information about the setting and what it does.

---

### ``DJANGO_STATIC_ROOT``

!!! example inline end ""

    This setting is **situational**.

See [``STATIC_ROOT`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#static-root) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_COOKIE_AGE``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_AGE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-age) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_COOKIE_DOMAIN``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_DOMAIN`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-domain) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_COOKIE_HTTPONLY``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_HTTPONLY`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-httponly) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_COOKIE_NAME``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-name) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_COOKIE_PATH``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_PATH`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-path) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_COOKIE_SAMESITE``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_SAMESITE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-samesite) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_COOKIE_SECURE``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_COOKIE_SECURE`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-cookie-secure) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_USE_SESSIONS``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_USE_SESSIONS`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-use-sessions) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_HEADER_NAME``

!!! question ""

    *This environment variable was added in DSMR-reader v6.0*

!!! example inline end ""

    This setting is **situational**.

Cross-Site Request Forgery (CSRF) related setting. Usually no customization needed, unless you're integrating DSMR-reader into another application.

See [``CSRF_HEADER_NAME`` in Django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-header-name) for more information about the setting and what it does.

---

### ``DJANGO_CSRF_TRUSTED_ORIGINS``

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
