# Changelog

!!! quote ""

    Before updating, make sure to check the changelog for any incompatible changes that may affect your installation.
    Usually only major version updates contain **incompatible changes**. E.g. upgrading from `v6.x` to `v7.x`.


---


## v6.1.0 - April 2026

<small>*Spring cleaning: improved accessibility, more reliable data retention and Dropbox sync, and a lighter frontend dependency footprint.*</small>

??? tip "Improvements"

    #### Accessibility
    - Applied WCAG 2.2 AA accessibility improvements to frontend templates (semantic headings, ARIA attributes, keyboard navigation, screen reader support)

    #### UI
    - Improved decimal rendering with ==experimental== formatting

    #### Retention
    - Improved retention data rotation query performance by using index-friendly count - [#2138](https://github.com/dsmrreader/dsmr-reader/issues/2138)
    - Improved retention data rotation scheduling to avoid redundant re-runs in steady state - [#2138](https://github.com/dsmrreader/dsmr-reader/issues/2138)
    - Improved retention data rotation to cache progress, skipping already-processed hours on subsequent runs - [#2138](https://github.com/dsmrreader/dsmr-reader/issues/2138)

    #### Dropbox
    - Improved Dropbox sync to no longer remove credentials on server/API errors, instead rescheduling for 5 minutes

??? abstract "Other changes and fixes"

    #### Fixes
    - Fixed retention data rotation being stuck in a loop on non-UTC systems (e.g. `Europe/Amsterdam`) - [#2137](https://github.com/dsmrreader/dsmr-reader/issues/2137)
    - Fixed empty green badges rendering on the energy contracts page when no electricity returned data is available - [#2133](https://github.com/dsmrreader/dsmr-reader/issues/2133)

    #### UI
    - Improved compare page trend icons and layout

    #### Dependencies
    - Updated Font Awesome Free from 7.1.0 to 7.2.0
    - Updated ECharts from 5.3.3 to 5.6.0
    - Updated jQuery from 3.6.0 to 3.7.1
    - Replaced Bootstrap Datepicker 1.9.0 with a custom day/month/year picker (Archive, Compare, Trends)
    - Replaced Moment.js with Day.js (~2 KB vs ~70 KB)
    - Removed unused vendored libraries: Semantic UI, iCheck, jQuery Inputmask, jQuery placeholder, jQuery slimScroll, jQuery ba-resize, Ionicons, html5shiv, Respond.js

    #### Miscellaneous
    - Generic development improvements


---


## v6.0.2 - February 2026

<small>*Reverts a PVOutput net power calculation change introduced in v6.0.0.*</small>

??? abstract "Fixes"
    
    #### PVOutput
    - ==Reverted v6.0 change== <del>[#2064](https://github.com/dsmrreader/dsmr-reader/pull/2064) Improved net power calculation to use **average** recent consumption data instead of latest value</del> - [#2131](https://github.com/dsmrreader/dsmr-reader/pull/2131)


---


## v6.0.1 - February 2026

<small>*Security dependency updates.*</small>

??? abstract "Fixes"
    
    #### Security

    - Updated dependencies due to security vulnerabilities - [#2109](https://github.com/dsmrreader/dsmr-reader/issues/2109) - [#2110](https://github.com/dsmrreader/dsmr-reader/issues/2110)


---


## v6.0.0 - February 2026

<small>*Major release dropping bare-metal installations, legacy database/Python versions, and old environment variables. Adds containerized hosting improvements, InfluxDB/MQTT queue management commands, and upgrades to Django 5.2 LTS.*</small>

??? danger "Incompatible changes"

    #### Incompatible changes: Installations
    Dropped installation support for:

    - ==Native/bare metal installations== without containers

    This project moves forward by adopting the containerized version of Xirixiz as the de facto standard installation method. 

    [DSMR-reader v6 upgrade guide](../how-to/upgrade/to-v6.md){ .md-button }

    <small>You can always host DSMR-reader yourself without containers and **without support**, as there are purposely no technical blockers built-in that prevent it. However, future releases will not take these installations into account and might break them unintentionally (e.g. with a Python upgrade). Care when chosing this route and manually updating in the future.</small>  
    
    ---

    #### Incompatible changes: Database versions
    Dropped database support for:

    - **PostgreSQL 10**
    - **PostgreSQL 11**
    - **PostgreSQL 12**
    - **PostgreSQL 13**
    - **MariaDB 10.1**
    - **MariaDB 10.2**
    - **MariaDB 10.3**
    - **MariaDB 10.4**
    - **MySQL 5.7** <small>(and lower)</small>
    - **MySQL 8.0.10** <small>(and lower)</small>

    <small>
    *Most database versions are [either end-of-life](https://www.postgresql.org/support/versioning/) or [no longer supported by the Django Framework](https://code.djangoproject.com/wiki/SupportedDatabaseVersions) version DSMR-reader uses (or will upgrade to in the upcoming year).*        
    *You are advised to upgrade to ==PostgreSQL 17== if you need to upgrade anyway. This will likely delay your next database upgrade required, for a few more years, as it's [expected to be end-of-life around late 2029](https://www.postgresql.org/support/versioning/).*
    </small>

    ---

    #### Incompatible changes: Python versions
    Dropped Python support for:

    - **Python 3.7**
    - **Python 3.8**
    - **Python 3.9**
    - **Python 3.10**
    - **Python 3.11**
    - **Python 3.12**

    <small>*DSMR-reader is developed, tested and built on Python 3.14. Older versions are unlikely to work due to dependency pinning.*</small>

    ---

    #### Incompatible changes: Legacy environment variables
    Dropped:

    - `DSMR_USER` <small>(replaced by `DSMRREADER_ADMIN_USER` since v5)</small>
    - `DSMR_PASSWORD` <small>(replaced by `DSMRREADER_ADMIN_PASSWORD` since v5)</small>
    - `DSMRREADER_BACKUP_INTERVAL_DAYS` <small>(replaced by admin setting since v5.9)</small>
    - `DSMRREADER_BACKUP_NAME_PREFIX` <small>(no replacement)</small>

    <small>*DSMR-reader is developed, tested and built on Python 3.13 and will soon even move to Python 3.14. Older versions are unlikely to work due to dependency pinning.*</small>

??? success "New features"

    #### Hosting
    - Added new dedicated URL route for health check and monitoring purposes:
        ```
        GET /healthcheck
        ```
    - More [Django settings](./environment-variables.md/#django-settingsoverrides) exposed via environment variables - [#2010](https://github.com/dsmrreader/dsmr-reader/issues/2010)
    - Added [``DSMRREADER_BACKEND_HIBERNATE``](./environment-variables.md/#dsmrreader_backend_hibernate) in favor of migrating to containerized setup

    <small>*This greatly improves the flexibility of changing internal settings without having to manually alter the installation.*</small>

    [All environment variables available](./environment-variables.md){ .md-button }

    ---

    #### InfluxDB
    - Use Influx URL instead of Influx hostname + port combination - [#1984](https://github.com/dsmrreader/dsmr-reader/issues/1984)
    - Added command-line alias for clearing InfluxDB queue
        - <small>*This is an alternative for executing database queries that do the same*</small>
        ```shell title="shell"
        ./manage.py dsmr_influxdb_clear_queue
        ```

    ---

    #### MQTT
    - Changed message queue primary key from AutoField to BigAutoField to reduce the number if sequence resets needed - [#2000](https://github.com/dsmrreader/dsmr-reader/issues/2000)
    - Added command-line alias for clearing MQTT queue
        - <small>*This is an alternative for executing database queries that do the same*</small>
        ```shell title="shell"
        ./manage.py dsmr_mqtt_clear_queue
        ```

??? abstract "Other changes and fixes"
    

    #### PVOutput
    - Improved net power calculation to use **average** recent consumption data instead of latest value - [#2064](https://github.com/dsmrreader/dsmr-reader/pull/2064)
    
    ---

    #### Documentation
    - Added explanation about upload time to MinderGas - [#1979](https://github.com/dsmrreader/dsmr-reader/issues/1979) by `MrLurch81`
    - Fixed broken API docs rendering caused by legacy ReDoc link
    - Simplified online documentation - [#1686](https://github.com/dsmrreader/dsmr-reader/issues/1686)
    - Dropped Dutch translation for the online documentation
        - <small>*The DSMR-reader translations inside the application are **not** affected*</small>
   
    ---

    #### Miscelaneous
    - Updated Django to 5.2 LTS
    - Updated a lot of other dependencies to a more recent version
        - <small>*The Dropbox SDK is the most important one due to incompatible Dropbox API changes per 1 January 2026*</small>
    - Updated FontAwesome icons assets to latest version
    - Added missing favicon for admin interface
    - Fixed some small typo's and translations

---

## Previous release series

<small>*Navigate between releases using the tabs below.*</small>

=== "v5.12"

    #### v5.12.0 - December 2025
    
    !!!+ warning
    
        This is the last release in the DSMR-reader v5.x series. Upgrade to DSMR-reader v6.x for future support and features.
    
        See the v6 upgrade guide for more information.
    
        [DSMR-reader v6 upgrade guide](../how-to/upgrade/to-v6.md){ .md-button .md-button--primary }
    
    - **Fixed** Updated Dropbox SDK to latest version in favor of incompatible API changes on January 1st, 2026.
    
    - **Changed** **Dropped** support for Python 3.7 and 3.8 - Do NOT update if you run these versions! Switch directly to DSMR-reader v6 instead.

=== "v5.11"
    
    #### v5.11.0 - February 2024
    
    - **Fixed** Bugfix for Archive which was causing the electricity returned meter positions to be displayed at all times.
    - **Fixed** [#1767](https://github.com/dsmrreader/dsmr-reader/issues/1767) Slightly alter debug info for unsupported database engines.
    - **Fixed** [#1841](https://github.com/dsmrreader/dsmr-reader/issues/1841) Restored broken `v4-upgrade-redirect` route for legacy upgrades.
    - **Fixed** [#1901](https://github.com/dsmrreader/dsmr-reader/issues/1901) Naming in sorted graphs configuration.
    - **Fixed** [#1945](https://github.com/dsmrreader/dsmr-reader/issues/1945) Make retention intervals more accurate. - by `RichieB2B`

    - **Changed** [#1827](https://github.com/dsmrreader/dsmr-reader/issues/1827) Update to python 3.11.2 - by `goegol`
    - **Changed** [#1861](https://github.com/dsmrreader/dsmr-reader/issues/1861) Added undocumented env var for low level datalogger usage

=== "v5.10"
    
    #### v5.10.4 - November 2023
    
    - **Fixed** [#1915](https://github.com/dsmrreader/dsmr-reader/issues/1915) Pyyaml dependency unavailable.
    
    #### v5.10.3 - February 2023
    
    - **Fixed** [#1799](https://github.com/dsmrreader/dsmr-reader/issues/1799) Bugfix in favor of `v5.10` DSMR-parser update (only affected Fluvius).
    
    #### v5.10.2 - January 2023
    
    - **Fixed** [#1770](https://github.com/dsmrreader/dsmr-reader/issues/1770) Disabled an automatic data migration in `v5.10` until further notice.
    
    #### v5.10.1 - January 2023
    
    - **Fixed** [#1795](https://github.com/dsmrreader/dsmr-reader/issues/1795) Bugfix in favor of `v5.10` data migration checks.
    
    #### v5.10.0 - January 2023
    
    - **Fixed** [#1770](https://github.com/dsmrreader/dsmr-reader/issues/1770) Fixed not always logging the right (gas) meter positions in day statistics correctly.
    - **Fixed** [#1770](https://github.com/dsmrreader/dsmr-reader/issues/1770) Fixed having gas consumption in day statistics being slightly off (situationally).
    - **Fixed** [#1792](https://github.com/dsmrreader/dsmr-reader/issues/1770) Fix dark mode warnings in Django admin
    - **Fixed** Fixed minor issues on the Dashboard notification page in favor of automatic migration messages.
    
    - **Added** [#1770](https://github.com/dsmrreader/dsmr-reader/issues/1770) Now tracking meter position timestamps in day statistics. Added them to Archive (day view) and Export.
    - **Added** [#1770](https://github.com/dsmrreader/dsmr-reader/issues/1770) Automatic migrations retroactively reassessing meter positions and timestamps. Additionally checks/fixes gas consumption mismatch.
    - **Added** [#1794](https://github.com/dsmrreader/dsmr-reader/issues/1794) Added new datalogger configuration option for selecting extra device channel for specific vendor(s)
    - **Added** Old Dashboard notifications can now be viewed and permanently deleted in the Frontend admin section.
    
    - **Changed** [#1725](https://github.com/dsmrreader/dsmr-reader/issues/1725) The value of `DSMRREADER_LOGLEVEL` is now restricted to: `DEBUG`, `WARNING` or `ERROR`
    - **Changed** [#1725](https://github.com/dsmrreader/dsmr-reader/issues/1725) The value of `DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD` is now restricted to: `serial` or `ipv4`
    - **Changed** [#1794](https://github.com/dsmrreader/dsmr-reader/issues/1794) [#1764](https://github.com/dsmrreader/dsmr-reader/issues/1764) Updated dsmr_parser (mostly) with latest version

=== "v5.9"

    #### v5.9.0 - November 2022

    - **Added** Support for Python 3.11
    - **Added** Added new "Support" page to access help and debugging information more easily
    - **Added** [#1635](https://github.com/dsmrreader/dsmr-reader/issues/1635) Support for quarter-hour peak consumption split-topic MQTT messages - Sent after a new quarter-hour peak is calculated
    - **Added** [#1635](https://github.com/dsmrreader/dsmr-reader/issues/1635) Support for quarter-hour peak consumption JSON MQTT messages - Sent after a new quarter-hour peak is calculated
    - **Added** [#1635](https://github.com/dsmrreader/dsmr-reader/issues/1635) New REST API endpoint for listing quarter-hour peak electricity consumption
    - **Added** [#1746](https://github.com/dsmrreader/dsmr-reader/issues/1746) [#1685](https://github.com/dsmrreader/dsmr-reader/issues/1685) New admin setting for changing backup intervals
    - **Added** [#1746](https://github.com/dsmrreader/dsmr-reader/issues/1746) [#1609](https://github.com/dsmrreader/dsmr-reader/issues/1609) New admin setting for changing backup file names
    
    ---
    
    - **Changed** Reworked API docs, updated Postman collection.
    - **Changed** Reworked "About" page, splitting it partially into the new "support" page.
    - **Changed** Reworked small GUI stuff, updated some icons.
    
    ---
    
    - **Removed** Dropped "Export" menu item from the main menu, added a reference to it on the new "Support" page instead.
    
    ---
    
    - **Deprecated** [#1685](https://github.com/dsmrreader/dsmr-reader/issues/1685) Prepared future removal of undocumented `DSMRREADER_BACKUP_INTERVAL_DAYS` env var for overriding backup intervals
    - **Deprecated** [#1609](https://github.com/dsmrreader/dsmr-reader/issues/1609) Prepared future removal of undocumented `DSMRREADER_BACKUP_NAME_PREFIX` env var for overriding backup name prefix
    
    > **Attention:**
    > The deprecated `DSMRREADER_BACKUP_INTERVAL_DAYS` and `DSMRREADER_BACKUP_NAME_PREFIX` env vars still take priority over the newly introduced admin settings.
    > However, please **remove** these env vars from your installation if you use them and just use the admin interface instead.

=== "v5.8"
    
    #### v5.8.0 - September 2022
    
    - **Fixed** [#1714](https://github.com/dsmrreader/dsmr-reader/issues/1714) Outgoing MQTT message queue not maintaining its own order
    
    > **Attention:**
    > This release fixes a four-year-old bug that may have disrupted the order of your MQTT messages sent by DSMR-reader.
    >
    > It only affected installations with either a high throughput of data or a delayed backend process (or both).
    > You probably may only have noticed it when running an installation similar to the one above, along using per-topic data sources.
    > The majority of users should be unaffected anyway.

=== "v5.7"

    #### v5.7.0 - September 2022
    
    - **Added** [#1685](https://github.com/dsmrreader/dsmr-reader/issues/1685) New undocumented `DSMRREADER_BACKUP_INTERVAL_DAYS` for overriding backup intervals - ⚠️ *Dropped again in future release*
     **Changed** [#1636](https://github.com/dsmrreader/dsmr-reader/issues/1636) Entire codebase reformatted with Black
    - **Changed** [#1711](https://github.com/dsmrreader/dsmr-reader/issues/1711) Use temperature instead of ground temperature from Buienradar API - by @mind04

=== "v5.6"

    #### v5.6.0 - August 2022

    - **Added** [#1635](https://github.com/dsmrreader/dsmr-reader/issues/1635) Added peak consumption live graph
    - **Changed** [#1635](https://github.com/dsmrreader/dsmr-reader/issues/1635) Reworked/improved peak consumption
    - **Changed** [#979](https://github.com/dsmrreader/dsmr-reader/issues/979) Deselect live electricity graph kWh totals by default

=== "v5.5"

    #### v5.5.1 - July 2022

    - **Fixed** [#1677](https://github.com/dsmrreader/dsmr-reader/issues/1677) Unable to configure dropbox backup - Dropbox SDK downgrade

    #### v5.5.0 - July 2022

    - **Added** [#979](https://github.com/dsmrreader/dsmr-reader/issues/979) Total kWh consumed/returned (diff) in live electricity graph
    - **Changed** [#1665](https://github.com/dsmrreader/dsmr-reader/issues/1665) Python patch bump + optimizations - by @goegol
    - **Changed** [#1666](https://github.com/dsmrreader/dsmr-reader/issues/1666) Tariefnamen rechttrekken
    - **Changed** [#1420](https://github.com/dsmrreader/dsmr-reader/issues/1420) Allow graph 'stack' option for live graphs
    - **Changed** [#979](https://github.com/dsmrreader/dsmr-reader/issues/979) Reworked live graphs a bit, dropped inverse graphs too

=== "v5.4"

    #### v5.4.0 - July 2022

    - **Changed** [#1390](https://github.com/dsmrreader/dsmr-reader/issues/1390) Pie charts in Trends vervangen door bar/line chart
    - **Changed** [#1652](https://github.com/dsmrreader/dsmr-reader/issues/1652) Energiecontracten makkelijker kunnen klonen
    - **Changed** [#1527](https://github.com/dsmrreader/dsmr-reader/issues/1527) Totaalverbruik toevoegen bij "Vergelijk"
    - **Changed** [#1646](https://github.com/dsmrreader/dsmr-reader/issues/1646) Added comment regarding MinderGas upload mechanism

=== "v5.3"

    #### v5.3.0 - June 2022

    - **Added** [#1640](https://github.com/dsmrreader/dsmr-reader/issues/1640) New API endpoint for fetching the energy supplier price (contracts) entered in DSMR-reader
    - **Changed** [#1640](https://github.com/dsmrreader/dsmr-reader/issues/1640) Updated/improved API documentation
    - **Changed** [#1623](https://github.com/dsmrreader/dsmr-reader/issues/1623) Improved Dropbox connection error handling a bit

=== "v5.2"

    #### v5.2.0 - May 2022
    
    - **Added** [#1084](https://github.com/dsmrreader/dsmr-reader/issues/1084) Support for tracking quarter peak electricity consumption *(due to upcoming changes in Belgium's policy)*
    - **Added** [#1559](https://github.com/dsmrreader/dsmr-reader/issues/1559) Meterstand tonen bij energiecontracten
    - **Added** [#1609](https://github.com/dsmrreader/dsmr-reader/issues/1609) Allow overriding backup files name prefix
    - **Changed** Added new admin setting for GUI refresh interval (1 - 5 seconds, default 5)
    - **Changed** Reworked search terms for Configuration page a bit
    - **Changed** Improved error logging for uncaught errors in backend process
    - **Changed** [#1612](https://github.com/dsmrreader/dsmr-reader/issues/1612) Added libjpeg-dev to upgrade guide for situational issues
    - **Fixed** [#1602](https://github.com/dsmrreader/dsmr-reader/issues/1602) Graph numbers hidden when using OS dark mode + DSMR-reader light mode
    - **Fixed** [#1631](https://github.com/dsmrreader/dsmr-reader/issues/1631) Meter statistics tariff description field update

=== "v5.1"

    #### v5.1.0 - March 2022
    
    !!! warning
    
        The following features/support were changed in an **incompatible** way due to external requirements!
    
    - **Changed** [#1210](https://github.com/dsmrreader/dsmr-reader/issues/1210) Dropbox Oauth flow: The App Key **is no longer configurable in the admin interface** and now uses the default App Key of DSMR-reader
    
    ---
    
    *Other changes*:
    
    - **Added** [#1567](https://github.com/dsmrreader/dsmr-reader/issues/1567) Support for dark mode - by @Justin991q
    - **Changed** [#1589](https://github.com/dsmrreader/dsmr-reader/issues/1589) Dagelijkse notificaties uitbreiden
    - **Changed** Trends datepicker start now defaults to today
    - **Changed** Extended some admin forms with additional delete/save/update buttons on top of page
    - **Changed** Added support for deleting "dsmrreading" records and "electricity/gas consumption" records in the admin
    - **Changed** Dependency updates
    - **Fixed** [dsmr-reader-docker/#1579](https://github.com/xirixiz/dsmr-reader-docker/issues/268) Increased remote datalogger its default log level from `INFO` to `ERROR`
    - **Fixed** [#1579](https://github.com/dsmrreader/dsmr-reader/issues/1579) Fix docker issue with pg_dump not found - by @sanderdw
    - **Fixed** [#1523](https://github.com/dsmrreader/dsmr-reader/issues/1523) Improved empty/error state in Trends
    - **Fixed** [#1517](https://github.com/dsmrreader/dsmr-reader/issues/1517) Vergelijken geeft visueel verkeerde kleur bij negatief verschil
    - **Fixed** [#1591](https://github.com/dsmrreader/dsmr-reader/issues/1591) Added headers to XHR responses to prevent browser caching

=== "v5.0"
    
    #### v5.0.0 - February 2022
    
    !!! note
    
        This release of DSMR-reader requires you to **manually upgrade** from `v4.x` to `v5.x`. See [the v5 upgrade guide](../how-to/upgrade/to-v5.md) for more information.
    
    ---
    
    !!! tip
    
        The following changes *may* affect your setup of DSMR-reader.
    
    - **Added** [#1314](https://github.com/dsmrreader/dsmr-reader/issues/1314) Added support for **Python 3.10**
    - **Added** [#1380](https://github.com/dsmrreader/dsmr-reader/issues/1380) Added support for **InfluxDB 2.x**
    
    ---
    
    - **Changed** [dsmr_datalogger_api_client.py](https://github.com/dsmrreader/dsmr-reader/blob/v5/dsmr_datalogger/scripts/dsmr_datalogger_api_client.py) env vars are now prefixed with `DSMRREADER_REMOTE_` (*affects new installations only*) [#1216](https://github.com/dsmrreader/dsmr-reader/issues/1216)
    - **Changed** [#1561](https://github.com/dsmrreader/dsmr-reader/issues/1561) The default value of `DSMRREADER_MQTT_MAX_CACHE_TIMEOUT` was changed from `3600` to `0`, disabling MQTT cache by default
    - **Changed** [#1561](https://github.com/dsmrreader/dsmr-reader/issues/1561) The default value of `DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE` was changed from `500` to `5000`
    - **Changed** [#1380](https://github.com/dsmrreader/dsmr-reader/issues/1380) The `dsmr_influxdb_export_all_readings` its console arguments were renamed due to **InfluxDB 2.x**
    - **Changed** [#1210](https://github.com/dsmrreader/dsmr-reader/issues/1210) Dropbox integratie via OAuth + PKCE
    - **Changed** [#1314](https://github.com/dsmrreader/dsmr-reader/issues/1314) Preferred Python version for DSMR-reader is now Python 3.9 (*support until end of 2025*), minimum version Python 3.7
    - **Changed** [#1363](https://github.com/dsmrreader/dsmr-reader/issues/1363) Updated to Django 3.2
    
    ---
    
    - **Fixed** [#1563](https://github.com/dsmrreader/dsmr-reader/issues/1563) OpenAPI specs wijken qua formaat af van de bestandsextensie
    - **Fixed** [#1568](https://github.com/dsmrreader/dsmr-reader/issues/1568) InfluxDB 2.x instelling-velden te kort (*release candidate 2*)
    
    ---
    
    > **Warning:**
    > ⚠️ The following features/support have been **dropped** or were changed in an **incompatible** way!
    
    - **Changed** [#1297](https://github.com/dsmrreader/dsmr-reader/issues/1297) Relocated Supervisor processes PID files from `/var/tmp/` to `/tmp/`
    - **Removed** [#1314](https://github.com/dsmrreader/dsmr-reader/issues/1314) Dropped support for **Python 3.6** (*EOL December 2021*)
    - **Removed** [#1380](https://github.com/dsmrreader/dsmr-reader/issues/1380) Dropped support for **InfluxDB 1.x**
    - **Removed** [#1363](https://github.com/dsmrreader/dsmr-reader/issues/1363) Dropped support for **PostgreSQL 9.x** and below (*due to Django 3.2* + PostgreSQL lifecycle)
    - **Removed** [#1363](https://github.com/dsmrreader/dsmr-reader/issues/1363) Dropped support for **MySQL 5.6** and below (*due to Django 3.2*)
    - **Removed** [#1210](https://github.com/dsmrreader/dsmr-reader/issues/1210) Dropped support for **legacy Dropbox tokens**, now using OAuth
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `SECRET_KEY` env var, use `DJANGO_SECRET_KEY` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DB_ENGINE` env var, use `DJANGO_DATABASE_ENGINE` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DB_NAME` env var, use `DJANGO_DATABASE_NAME` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DB_USER` env var, use `DJANGO_DATABASE_USER` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DB_PASS` env var, use `DJANGO_DATABASE_PASSWORD` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DB_HOST` env var, use `DJANGO_DATABASE_HOST` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DB_PORT` env var, use `DJANGO_DATABASE_PORT` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `CONN_MAX_AGE` env var, use `DJANGO_DATABASE_CONN_MAX_AGE` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `TZ` env var, use `DJANGO_TIME_ZONE` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DSMR_USER` env var, use `DSMRREADER_ADMIN_USER` instead
    - **Removed** [#1141](https://github.com/dsmrreader/dsmr-reader/issues/1141) Dropped `DSMR_PASSWORD` env var, use `DSMRREADER_ADMIN_PASSWORD` instead
    - **Removed** Dropped `DATALOGGER_INPUT_METHOD` env var, use `DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD` instead
    - **Removed** Dropped `DATALOGGER_SERIAL_PORT` env var, use `DSMRREADER_REMOTE_DATALOGGER_SERIAL_PORT` instead
    - **Removed** Dropped `DATALOGGER_SERIAL_BAUDRATE` env var, use `DSMRREADER_REMOTE_DATALOGGER_SERIAL_BAUDRATE` instead
    - **Removed** Dropped `DATALOGGER_API_HOSTS` env var, use `DSMRREADER_REMOTE_DATALOGGER_API_HOSTS` instead
    - **Removed** Dropped `DATALOGGER_API_KEYS` env var, use `DSMRREADER_REMOTE_DATALOGGER_API_KEYS` instead
    - **Removed** Dropped `DATALOGGER_TIMEOUT` env var, use `DSMRREADER_REMOTE_DATALOGGER_TIMEOUT` instead
    - **Removed** Dropped `DATALOGGER_SLEEP` env var, use `DSMRREADER_REMOTE_DATALOGGER_SLEEP` instead
    - **Removed** Dropped `DATALOGGER_MIN_SLEEP_FOR_RECONNECT` env var, use `DSMRREADER_REMOTE_DATALOGGER_MIN_SLEEP_FOR_RECONNECT` instead

---

*Changelogs of older versions can be found in the DSMR-reader GitHub repository*.
