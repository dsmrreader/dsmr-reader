Changelog
=========


.. contents::
    :depth: 2



Upgrading
^^^^^^^^^
Please make sure you have a fresh **database backup** before upgrading! Upgrading is very easy due to a builtin mechanism. 

.. seealso:: 

    - `About back-ups <http://dsmr-reader.readthedocs.io/en/latest/application.html#data-preservation-backups>`_.
    - `About upgrading <http://dsmr-reader.readthedocs.io/en/latest/application.html#application-updates-bug-fixes-new-features>`_.



v1.14.0 - 2018-xx-xx
^^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#xxxxxxx <https://github.com/dennissiemensma/dsmr-reader/issues/xxxxxx>`_] xxxxxxxxx



v1.13.0 - 2018-01-23
^^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#203 <https://github.com/dennissiemensma/dsmr-reader/issues/203>`_] One-click installer
- [`#396 <https://github.com/dennissiemensma/dsmr-reader/issues/396>`_] Gecombineerd tarief tonen op 'Statistieken'-pagina
- [`#268 <https://github.com/dennissiemensma/dsmr-reader/issues/268>`_] Data preservation/backups - by WatskeBart
- [`#425 <https://github.com/dennissiemensma/dsmr-reader/issues/425>`_] Requests for donating a beer or coffee
- [`#427 <https://github.com/dennissiemensma/dsmr-reader/issues/427>`_] Reconnect to postgresql
- [`#394 <https://github.com/dennissiemensma/dsmr-reader/issues/394>`_] Django 2.0 


v1.12.0 - 2018-01-14
^^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#72 <https://github.com/dennissiemensma/dsmr-reader/issues/72>`_] Source data retention
- [`#414 <https://github.com/dennissiemensma/dsmr-reader/issues/414>`_] add systemd service files - by meijjaa
- [`#405 <https://github.com/dennissiemensma/dsmr-reader/issues/405>`_] More updates to the Dutch translation of the documentation - by lckarssen
- [`#404 <https://github.com/dennissiemensma/dsmr-reader/issues/404>`_] Fix minor typo in Dutch translation - by lckarssen
- [`#398 <https://github.com/dennissiemensma/dsmr-reader/issues/398>`_] iOS Web App: prevent same-window links from being opened externally - by Joris Vervuurt
- [`#399 <https://github.com/dennissiemensma/dsmr-reader/issues/399>`_] Veel calls naar api.buienradar
- [`#406 <https://github.com/dennissiemensma/dsmr-reader/issues/406>`_] Spelling correction trends page
- [`#413 <https://github.com/dennissiemensma/dsmr-reader/issues/413>`_] Hoge CPU belasting op rpi 2 icm DSMR 5.0 meter
- [`#419 <https://github.com/dennissiemensma/dsmr-reader/issues/419>`_] Requirements update (January 2018)



v1.11.0 - 2017-11-24
^^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#382 <https://github.com/dennissiemensma/dsmr-reader/issues/382>`_] Archief klopt niet
- [`#385 <https://github.com/dennissiemensma/dsmr-reader/issues/385>`_] Ververs dagverbruik op dashboard automatisch - by HugoDaBosss
- [`#387 <https://github.com/dennissiemensma/dsmr-reader/issues/387>`_] There are too many unprocessed telegrams - by HugoDaBosss
- [`#368 <https://github.com/dennissiemensma/dsmr-reader/issues/368>`_] Gebruik van os.environ.get - by ju5t
- [`#370 <https://github.com/dennissiemensma/dsmr-reader/issues/370>`_] Pvoutput upload zonder teruglevering
- [`#371 <https://github.com/dennissiemensma/dsmr-reader/issues/371>`_] fonts via https laden
- [`#378 <https://github.com/dennissiemensma/dsmr-reader/issues/378>`_] Processing of telegrams stalled



v1.10.0 - 2017-10-19
^^^^^^^^^^^^^^^^^^^^

.. note::

   This releases turns telegram logging **off by default**. 
   If you wish to continue using this feature, add ``DSMRREADER_LOG_TELEGRAMS = True`` to your ``settings.py`` and reload the application.


**Tickets resolved in this release:**

- [`#363 <https://github.com/dennissiemensma/dsmr-reader/issues/363>`_] Show electricity_merged in the Total row for current month - by helmo
- [`#305 <https://github.com/dennissiemensma/dsmr-reader/issues/305>`_] Trend staafdiagrammen afgelopen week / afgelopen maand altijd gelijk
- [`#194 <https://github.com/dennissiemensma/dsmr-reader/issues/194>`_] Add timestamp to highest and lowest Watt occurance
- [`#365 <https://github.com/dennissiemensma/dsmr-reader/issues/365>`_] Turn telegram logging off by default
- [`#366 <https://github.com/dennissiemensma/dsmr-reader/issues/366>`_] Restructure docs



v1.9.0 - 2017-10-08
^^^^^^^^^^^^^^^^^^^

.. note::

    This release contains an update for the API framework, which `has a fix for some timezone issues <https://github.com/encode/django-rest-framework/issues/3732>`_.
    You may experience different output regarding to datetime formatting when using the API.


**Tickets resolved in this release:**

- [`#9 <https://github.com/dennissiemensma/dsmr-reader/issues/9>`_] Data export: PVOutput
- [`#163 <https://github.com/dennissiemensma/dsmr-reader/issues/163>`_] Allow separate prices/costs for electricity returned
- [`#337 <https://github.com/dennissiemensma/dsmr-reader/issues/337>`_] API mogelijkheid voor ophalen 'dashboard' waarden
- [`#284 <https://github.com/dennissiemensma/dsmr-reader/issues/284>`_] Automatische backups geven alleen lege bestanden
- [`#279 <https://github.com/dennissiemensma/dsmr-reader/issues/279>`_] Weather report with temperature '-' eventually results in stopped dsmr_backend
- [`#245 <https://github.com/dennissiemensma/dsmr-reader/issues/245>`_] Grafiek gasverbruik doet wat vreemd na aantal uur geen nieuwe data
- [`#272 <https://github.com/dennissiemensma/dsmr-reader/issues/272>`_] Dashboard - weergave huidig verbruik bij smalle weergave
- [`#273 <https://github.com/dennissiemensma/dsmr-reader/issues/273>`_] Docker (by xirixiz) reference in docs
- [`#286 <https://github.com/dennissiemensma/dsmr-reader/issues/286>`_] Na gebruik admin-pagina's geen (eenvoudige) mogelijkheid voor terugkeren naar de site
- [`#332 <https://github.com/dennissiemensma/dsmr-reader/issues/332>`_] Launch full screen on iOS device when opening from homescreen
- [`#276 <https://github.com/dennissiemensma/dsmr-reader/issues/276>`_] Display error compare page on mobile
- [`#288 <https://github.com/dennissiemensma/dsmr-reader/issues/288>`_] Add info to FAQ
- [`#320 <https://github.com/dennissiemensma/dsmr-reader/issues/320>`_] auto refresh op statussen op statuspagina
- [`#314 <https://github.com/dennissiemensma/dsmr-reader/issues/314>`_] Add web-applicatie mogelijkheid ala pihole
- [`#358 <https://github.com/dennissiemensma/dsmr-reader/issues/358>`_] Requirements update (September 2017)
- [`#270 <https://github.com/dennissiemensma/dsmr-reader/issues/270>`_] Public Webinterface Warning (readthedocs.io)
- [`#231 <https://github.com/dennissiemensma/dsmr-reader/issues/231>`_] Contributors update
- [`#300 <https://github.com/dennissiemensma/dsmr-reader/issues/300>`_] Upgrade to Django 1.11 LTS
 


v1.8.2 - 2017-08-12
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#346 <https://github.com/dennissiemensma/dsmr-reader/issues/346>`_] Defer statistics page XHR 



v1.8.1 - 2017-07-04
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#339 <https://github.com/dennissiemensma/dsmr-reader/issues/339>`_] Upgrade Dropbox-client to v8.x 



v1.8.0 - 2017-06-14
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#141 <https://github.com/dennissiemensma/dsmr-reader/issues/141>`_] Add MQTT support to publish readings
- [`#331 <https://github.com/dennissiemensma/dsmr-reader/issues/331>`_] Requirements update (June 2016)
- [`#299 <https://github.com/dennissiemensma/dsmr-reader/issues/299>`_] Support Python 3.6



v1.7.0 - 2017-05-04
^^^^^^^^^^^^^^^^^^^

.. warning::

    Please note that the ``dsmr_datalogger.0007_dsmrreading_timestamp_index`` migration **will take quite some time**, as it adds an index on one of the largest database tables!
    
    It takes **around two minutes** on a RaspberryPi 2 & 3 with ``> 4.3 million`` readings on PostgreSQL. Results may differ on **slower RaspberryPi's** or **with MySQL**.


.. note::

    The API-docs for the new v2 API `can be found here <https://dsmr-reader.readthedocs.io/en/latest/api.html>`_.


**Tickets resolved in this release:**

- [`#230 <https://github.com/dennissiemensma/dsmr-reader/issues/230>`_] Support for exporting data via API



v1.6.2 - 2017-04-23
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#269 <https://github.com/dennissiemensma/dsmr-reader/issues/269>`_] x-as gasgrafiek geeft rare waarden aan
- [`#303 <https://github.com/dennissiemensma/dsmr-reader/issues/303>`_] Archive page's default day sorting



v1.6.1 - 2017-04-06
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- [`#298 <https://github.com/dennissiemensma/dsmr-reader/issues/298>`_] Update requirements (Django 1.10.7)



v1.6.0 - 2017-03-18
^^^^^^^^^^^^^^^^^^^

.. warning::

    Support for ``MySQL`` has been **deprecated** since ``DSMR-reader v1.6`` and will be discontinued completely in a later release.
    Please use a PostgreSQL database instead. Users already running MySQL will be supported in easily migrating to PostgreSQL in the future.

.. note::

    **Change in API:**
    The telegram creation API now returns an ``HTTP 201`` response when successful.
    An ``HTTP 200`` was returned in former versions.
    :doc:`View API docs<api>`.


**Tickets resolved in this release:**

- [`#221 <https://github.com/dennissiemensma/dsmr-reader/issues/221>`_] Support for DSMR-firmware v5.0.
- [`#237 <https://github.com/dennissiemensma/dsmr-reader/issues/237>`_] Redesign: Status page.
- [`#249 <https://github.com/dennissiemensma/dsmr-reader/issues/249>`_] Req: Add iOS icon for Bookmark.
- [`#232 <https://github.com/dennissiemensma/dsmr-reader/issues/232>`_] Docs: Explain settings/options.
- [`#260 <https://github.com/dennissiemensma/dsmr-reader/issues/260>`_] Add link to readthedocs in Django for Dropbox instructions.
- [`#211 <https://github.com/dennissiemensma/dsmr-reader/issues/211>`_] API request should return HTTP 201 instead of HTTP 200.
- [`#191 <https://github.com/dennissiemensma/dsmr-reader/issues/191>`_] Deprecate MySQL support.
- [`#251 <https://github.com/dennissiemensma/dsmr-reader/issues/251>`_] Buienradar Uncaught exception.
- [`#257 <https://github.com/dennissiemensma/dsmr-reader/issues/257>`_] Requirements update (February 2017).
- [`#274 <https://github.com/dennissiemensma/dsmr-reader/issues/274>`_] Requirements update (March 2017).



v1.5.5 - 2017-01-19
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- Remove readonly restriction for editing statistics in admin interface (`#242 <https://github.com/dennissiemensma/dsmr-reader/issues/242>`_).



v1.5.4 - 2017-01-12
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- Improve datalogger for DSMR v5.0 (`#212 <https://github.com/dennissiemensma/dsmr-reader/issues/212>`_).
- Fixed another bug in MinderGas API client implementation (`#228 <https://github.com/dennissiemensma/dsmr-reader/issues/228>`_).



v1.5.5 - 2017-01-19
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- Remove readonly restriction for editing statistics in admin interface (`#242 <https://github.com/dennissiemensma/dsmr-reader/issues/242>`_).



v1.5.4 - 2017-01-12
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- Improve datalogger for DSMR v5.0 (`#212 <https://github.com/dennissiemensma/dsmr-reader/issues/212>`_).
- Fixed another bug in MinderGas API client implementation (`#228 <https://github.com/dennissiemensma/dsmr-reader/issues/228>`_).



v1.5.3 - 2017-01-11
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- Improve MinderGas API client implementation (`#228 <https://github.com/dennissiemensma/dsmr-reader/issues/228>`_).



v1.5.2 - 2017-01-09
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- Automatic refresh of dashboard charts (`#210 <https://github.com/dennissiemensma/dsmr-reader/issues/210>`_).
- Mindergas.nl API: Tijdstip van verzending willekeurig maken (`#204 <https://github.com/dennissiemensma/dsmr-reader/issues/204>`_).
- Extend API docs with additional example (`#185 <https://github.com/dennissiemensma/dsmr-reader/issues/185>`_).
- Docs: How to restore backup (`#190 <https://github.com/dennissiemensma/dsmr-reader/issues/190>`_).
- Log errors occured to file (`#181 <https://github.com/dennissiemensma/dsmr-reader/issues/181>`_).



v1.5.1 - 2017-01-04
^^^^^^^^^^^^^^^^^^^

.. note::

    This patch contains no new features and **only solves upgrading issues** for some users.


**Tickets resolved in this release:**

- Fix for issues `#200 <https://github.com/dennissiemensma/dsmr-reader/issues/200>`_ & `#217 <https://github.com/dennissiemensma/dsmr-reader/issues/217>`_, which is caused by omitting the switch to the VirtualEnv. This was not documented well enough in early versions of this project, causing failed upgrades. 



v1.5.0 - 2017-01-01
^^^^^^^^^^^^^^^^^^^

.. warning:: **Change in Python support** 

  - The support for ``Python 3.3`` has been **dropped** due to the Django upgrade (`#103 <https://github.com/dennissiemensma/dsmr-reader/issues/103>`_).
  - There is **experimental support** for ``Python 3.6`` and ``Python 3.7 (nightly)`` as the unittests are `now built against those versions <https://travis-ci.org/dennissiemensma/dsmr-reader/branches>`_ as well (`#167 <https://github.com/dennissiemensma/dsmr-reader/issues/167>`_). 

.. warning:: **Legacy warning**

  - The migrations that were squashed together in (`#31 <https://github.com/dennissiemensma/dsmr-reader/issues/31>`_) have been **removed**. This will only affect you when you are currently still running a dsmrreader-version of **before** ``v0.13 (β)``. 
  - If you are indeed still running ``< v0.13 (β)``, please upgrade to ``v1.4`` first (!), followed by an upgrade to ``v1.5``. 

**Tickets resolved in this release:**

- Verify telegrams' CRC (`#188 <https://github.com/dennissiemensma/dsmr-reader/issues/188>`_).
- Display last 24 hours on dashboard (`#164 <https://github.com/dennissiemensma/dsmr-reader/issues/164>`_).
- Status page visualisation (`#172 <https://github.com/dennissiemensma/dsmr-reader/issues/172>`_).
- Store and display phases consumption (`#161 <https://github.com/dennissiemensma/dsmr-reader/issues/161>`_).
- Weather graph not showing when no gas data is available (`#170 <https://github.com/dennissiemensma/dsmr-reader/issues/170>`_).
- Upgrade to ChartJs 2.0 (`#127 <https://github.com/dennissiemensma/dsmr-reader/issues/127>`_).
- Improve Statistics page performance (`#173 <https://github.com/dennissiemensma/dsmr-reader/issues/173>`_).
- Version checker at github (`#166 <https://github.com/dennissiemensma/dsmr-reader/issues/166>`_).
- Remove required login for dismissal of in-app notifications (`#179 <https://github.com/dennissiemensma/dsmr-reader/issues/179>`_).
- Round numbers displayed in GUI to 2 decimals (`#183 <https://github.com/dennissiemensma/dsmr-reader/issues/183>`_).
- Switch Nosetests to Pytest (+ pytest-cov) (`#167 <https://github.com/dennissiemensma/dsmr-reader/issues/167>`_).
- PyLama code audit (+ pytest-cov) (`#158 <https://github.com/dennissiemensma/dsmr-reader/issues/158>`_).
- Double upgrade of Django framework ``Django 1.8`` -> ``Django 1.9`` -> ``Django 1.10`` (`#103 <https://github.com/dennissiemensma/dsmr-reader/issues/103>`_).
- Force ``PYTHONUNBUFFERED`` for supervisor commands (`#176 <https://github.com/dennissiemensma/dsmr-reader/issues/176>`_).
- Documentation updates for v1.5 (`#171 <https://github.com/dennissiemensma/dsmr-reader/issues/171>`_).
- Requirements update for v1.5 (december 2016) (`#182 <https://github.com/dennissiemensma/dsmr-reader/issues/182>`_).
- Improved backend process logging (`#184 <https://github.com/dennissiemensma/dsmr-reader/issues/184>`_).



v1.4.1 - 2016-12-12
^^^^^^^^^^^^^^^^^^^

**Tickets resolved in this release:**

- Consumption chart hangs due to unique_key violation (`#174 <https://github.com/dennissiemensma/dsmr-reader/issues/174>`_).
- NoReverseMatch at / Reverse for 'docs' (`#175 <https://github.com/dennissiemensma/dsmr-reader/issues/175>`_).



v1.4.0 - 2016-11-28
^^^^^^^^^^^^^^^^^^^
.. warning:: **Change in Python support**

  - Support for ``Python 3.5`` has been added officially (`#55 <https://github.com/dennissiemensma/dsmr-reader/issues/55>`_).

**Tickets resolved in this release:**

- Push notifications for Notify My Android / Prowl (iOS), written by Jeroen Peters (`#152 <https://github.com/dennissiemensma/dsmr-reader/issues/152>`_).
- Support for both single and high/low tariff (`#130 <https://github.com/dennissiemensma/dsmr-reader/issues/130>`_).
- Add new note from Dashboard has wrong time format (`#159 <https://github.com/dennissiemensma/dsmr-reader/issues/159>`_).
- Display estimated price for current usage in Dashboard (`#155 <https://github.com/dennissiemensma/dsmr-reader/issues/155>`_).
- Dropbox API v1 deprecated in June 2017 (`#142 <https://github.com/dennissiemensma/dsmr-reader/issues/142>`_).
- Improve code coverage (`#151 <https://github.com/dennissiemensma/dsmr-reader/issues/151>`_).
- Restyle configuration overview (`#156 <https://github.com/dennissiemensma/dsmr-reader/issues/156>`_).
- Capability based push notifications (`#165 <https://github.com/dennissiemensma/dsmr-reader/issues/165>`_).



v1.3.2 - 2016-11-08
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- Requirements update (november 2016) (`#150 <https://github.com/dennissiemensma/dsmr-reader/issues/150>`_).



v1.3.1 - 2016-08-16
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- CSS large margin-bottom (`#144 <https://github.com/dennissiemensma/dsmr-reader/issues/144>`_).
- Django security releases issued: 1.8.14 (`#147 <https://github.com/dennissiemensma/dsmr-reader/issues/147>`_).
- Requirements update (August 2016) (`#148 <https://github.com/dennissiemensma/dsmr-reader/issues/148>`_).
- Query performance improvements (`#149 <https://github.com/dennissiemensma/dsmr-reader/issues/149>`_).



v1.3.0 - 2016-07-15
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- API endpoint for datalogger (`#140 <https://github.com/dennissiemensma/dsmr-reader/issues/140>`_).
- Colors for charts (`#137 <https://github.com/dennissiemensma/dsmr-reader/issues/137>`_).
- Data export: Mindergas.nl (`#10 <https://github.com/dennissiemensma/dsmr-reader/issues/10>`_).
- Requirement upgrade (`#143 <https://github.com/dennissiemensma/dsmr-reader/issues/143>`_).
- Installation wizard for first time use (`#139 <https://github.com/dennissiemensma/dsmr-reader/issues/139>`_).



v1.2.0 - 2016-05-18
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- Energy supplier prices does not indicate tariff type (Django admin) (`#126 <https://github.com/dennissiemensma/dsmr-reader/issues/126>`_).
- Requirements update (`#128 <https://github.com/dennissiemensma/dsmr-reader/issues/128>`_).
- Force backup (`#123 <https://github.com/dennissiemensma/dsmr-reader/issues/123>`_).
- Update clean-install.md (`#131 <https://github.com/dennissiemensma/dsmr-reader/issues/131>`_).
- Improve data export field names (`#132 <https://github.com/dennissiemensma/dsmr-reader/issues/132>`_).
- Display average temperature in archive (`#122 <https://github.com/dennissiemensma/dsmr-reader/issues/122>`_).
- Pie charts on trends page overlap their canvas (`#136 <https://github.com/dennissiemensma/dsmr-reader/issues/136>`_).
- 'Slumber' consumption (`#115 <https://github.com/dennissiemensma/dsmr-reader/issues/115>`_).
- Show lowest & highest Watt peaks (`#138 <https://github.com/dennissiemensma/dsmr-reader/issues/138>`_).
- Allow day & hour statistics reset due to changing energy prices (`#95 <https://github.com/dennissiemensma/dsmr-reader/issues/95>`_).



v1.1.2 - 2016-05-01
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- Trends page giving errors (when lacking data) (`#125 <https://github.com/dennissiemensma/dsmr-reader/issues/125>`_).



v1.1.1 - 2016-04-27
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- Improve readme (`#124 <https://github.com/dennissiemensma/dsmr-reader/issues/124>`_).



v1.1.0 - 2016-04-23
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- Autorefresh dashboard (`#117 <https://github.com/dennissiemensma/dsmr-reader/issues/117>`_).
- Improve line graphs' visibility (`#111 <https://github.com/dennissiemensma/dsmr-reader/issues/111>`_).
- Easily add notes (`#110 <https://github.com/dennissiemensma/dsmr-reader/issues/110>`_).
- Export data points in CSV format (`#2 <https://github.com/dennissiemensma/dsmr-reader/issues/2>`_).
- Allow day/month/year comparison (`#94 <https://github.com/dennissiemensma/dsmr-reader/issues/94>`_).
- Docs: Add FAQ and generic application info (`#113 <https://github.com/dennissiemensma/dsmr-reader/issues/113>`_).
- Support for Iskra meter (DSMR 2.x) (`#120 <https://github.com/dennissiemensma/dsmr-reader/issues/120>`_).



v1.0.1 - 2016-04-07
^^^^^^^^^^^^^^^^^^^
**Tickets resolved in this release:**

- Update licence to OSI compatible one (`#119 <https://github.com/dennissiemensma/dsmr-reader/issues/119>`_).



v1.0.0 - 2016-04-07
^^^^^^^^^^^^^^^^^^^
- First official stable release.



[β] v0.1 (2015-10-29) to 0.16 (2016-04-06)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

    All previous beta releases/changes have been combined to a single list below.

- Move documentation to wiki or RTD (`#90 <https://github.com/dennissiemensma/dsmr-reader/issues/90>`_).
- Translate README to Dutch (`#16 <https://github.com/dennissiemensma/dsmr-reader/issues/16>`_).
- Delete (recent) history page (`#112 <https://github.com/dennissiemensma/dsmr-reader/issues/112>`_).
- Display most recent temperature in dashboard (`#114 <https://github.com/dennissiemensma/dsmr-reader/issues/114>`_).
- Upgrade Django to 1.8.12 (`#118 <https://github.com/dennissiemensma/dsmr-reader/issues/118>`_).

- Redesign trends page (`#97 <https://github.com/dennissiemensma/dsmr-reader/issues/97>`_).
- Support for summer time (`#105 <https://github.com/dennissiemensma/dsmr-reader/issues/105>`_).
- Support for Daylight Saving Time (DST) transition (`#104 <https://github.com/dennissiemensma/dsmr-reader/issues/104>`_).
- Add (error) hints to status page (`#106 <https://github.com/dennissiemensma/dsmr-reader/issues/106>`_).
- Keep track of version (`#108 <https://github.com/dennissiemensma/dsmr-reader/issues/108>`_).

- Django 1.8.11 released (`#82 <https://github.com/dennissiemensma/dsmr-reader/issues/82>`_).
- Prevent tests from failing due to moment of execution (`#88 <https://github.com/dennissiemensma/dsmr-reader/issues/88>`_).
- Statistics page meter positions are broken (`#93 <https://github.com/dennissiemensma/dsmr-reader/issues/93>`_).
- Archive only shows graph untill 23:00 (11 pm) (`#77 <https://github.com/dennissiemensma/dsmr-reader/issues/77>`_).
- Trends page crashes due to nullable fields average (`#100 <https://github.com/dennissiemensma/dsmr-reader/issues/100>`_).
- Trends: Plot peak and off-peak relative to each other (`#99 <https://github.com/dennissiemensma/dsmr-reader/issues/99>`_).
- Monitor requirements with requires.io (`#101 <https://github.com/dennissiemensma/dsmr-reader/issues/101>`_).
- Terminology (`#41 <https://github.com/dennissiemensma/dsmr-reader/issues/41>`_).
- Obsolete signals in dsmr_consumption (`#63 <https://github.com/dennissiemensma/dsmr-reader/issues/63>`_).
- Individual app testing coverage (`#64 <https://github.com/dennissiemensma/dsmr-reader/issues/64>`_).
- Support for extra devices on other M-bus (0-n:24.1) (`#92 <https://github.com/dennissiemensma/dsmr-reader/issues/92>`_).
- Separate post-deployment commands (`#102 <https://github.com/dennissiemensma/dsmr-reader/issues/102>`_).

- Show exceptions in production (webinterface) (`#87 <https://github.com/dennissiemensma/dsmr-reader/issues/87>`_).
- Keep Supervisor processes running (`#79 <https://github.com/dennissiemensma/dsmr-reader/issues/79>`_).
- Hourly stats of 22:00:00+00 every day lack gas (`#78 <https://github.com/dennissiemensma/dsmr-reader/issues/78>`_).
- Test Travis-CI with MySQL + MariaDB + PostgreSQL (`#54 <https://github.com/dennissiemensma/dsmr-reader/issues/54>`_).
- PostgreSQL tests + nosetests + coverage failure: unrecognized configuration parameter "foreign_key_checks" (`#62 <https://github.com/dennissiemensma/dsmr-reader/issues/62>`_).
- Performance check (`#83 <https://github.com/dennissiemensma/dsmr-reader/issues/83>`_).
- Allow month & year archive (`#66 <https://github.com/dennissiemensma/dsmr-reader/issues/66>`_).
- Graphs keep increasing height on tablet (`#89 <https://github.com/dennissiemensma/dsmr-reader/issues/89>`_).

- Delete StatsSettings(.track) settings model (`#71 <https://github.com/dennissiemensma/dsmr-reader/issues/71>`_).
- Drop deprecated commands (`#22 <https://github.com/dennissiemensma/dsmr-reader/issues/22>`_).
- Datalogger doesn't work properly with DSMR 4.2 (KAIFA-METER) (`#73 <https://github.com/dennissiemensma/dsmr-reader/issues/73>`_).
- Dashboard month statistics costs does not add up (`#75 <https://github.com/dennissiemensma/dsmr-reader/issues/75>`_).
- Log unhandled exceptions and errors (`#65 <https://github.com/dennissiemensma/dsmr-reader/issues/65>`_).
- Datalogger crashes with IntegrityError because 'timestamp' is null (`#74 <https://github.com/dennissiemensma/dsmr-reader/issues/74>`_).
- Trends are always shown in UTC (`#76 <https://github.com/dennissiemensma/dsmr-reader/issues/76>`_).
- Squash migrations (`#31 <https://github.com/dennissiemensma/dsmr-reader/issues/31>`_).
- Display 'electricity returned' graph in dashboard (`#81 <https://github.com/dennissiemensma/dsmr-reader/issues/81>`_).
- Optional gas (and electricity returned) capabilities tracking (`#70 <https://github.com/dennissiemensma/dsmr-reader/issues/70>`_).
- Add 'electricity returned' to trends page (`#84 <https://github.com/dennissiemensma/dsmr-reader/issues/84>`_).

- Archive: View past days details (`#61 <https://github.com/dennissiemensma/dsmr-reader/issues/61>`_).
- Dashboard: Consumption total for current month (`#60 <https://github.com/dennissiemensma/dsmr-reader/issues/60>`_).
- Check whether gas readings are optional (`#34 <https://github.com/dennissiemensma/dsmr-reader/issues/34>`_).
- Django security releases issued: 1.8.10 (`#68 <https://github.com/dennissiemensma/dsmr-reader/issues/68>`_).
- Notes display in archive (`#69 <https://github.com/dennissiemensma/dsmr-reader/issues/69>`_).

- Status page/alerts when features are disabled/unavailable (`#45 <https://github.com/dennissiemensma/dsmr-reader/issues/45>`_).
- Integrate Travis CI (`#48 <https://github.com/dennissiemensma/dsmr-reader/issues/48>`_).
- Testing coverage (`#38 <https://github.com/dennissiemensma/dsmr-reader/issues/38>`_).
- Implement automatic backups & Dropbox cloud storage (`#44 <https://github.com/dennissiemensma/dsmr-reader/issues/44>`_).
- Link code coverage service to repository (`#56 <https://github.com/dennissiemensma/dsmr-reader/issues/56>`_).
- Explore timezone.localtime() as replacement for datetime.astimezone() (`#50 <https://github.com/dennissiemensma/dsmr-reader/issues/50>`_).
- Align GasConsumption.read_at to represent the start of hour (`#40 <https://github.com/dennissiemensma/dsmr-reader/issues/40>`_).

- Cleanup unused static files (`#47 <https://github.com/dennissiemensma/dsmr-reader/issues/47>`_).
- Investigated mysql_tzinfo_to_sql — Load the Time Zone Tables (`#35 <https://github.com/dennissiemensma/dsmr-reader/issues/35>`_).
- Make additional DSMR data optional (`#46 <https://github.com/dennissiemensma/dsmr-reader/issues/46>`_).
- Localize graph x-axis (`#42 <https://github.com/dennissiemensma/dsmr-reader/issues/42>`_).
- Added graph formatting string to gettext file (`#42 <https://github.com/dennissiemensma/dsmr-reader/issues/42>`_).
- Different colors for peak & off-peak electricity (`#52 <https://github.com/dennissiemensma/dsmr-reader/issues/52>`_).
- Admin: Note widget (`#51 <https://github.com/dennissiemensma/dsmr-reader/issues/51>`_).
- Allow GUI to run without data (`#26 <https://github.com/dennissiemensma/dsmr-reader/issues/26>`_).

- Moved project to GitHub (`#28 <https://github.com/dennissiemensma/dsmr-reader/issues/28>`_).
- Added stdout to dsmr_backend to reflect progress.
- Restore note usage in GUI (`#39 <https://github.com/dennissiemensma/dsmr-reader/issues/39>`_).

- Store daily, weekly, monthly and yearly statistics (`#3 <https://github.com/dennissiemensma/dsmr-reader/issues/3>`_).
- Improved Recent History page performance a bit. (as result of `#3 <https://github.com/dennissiemensma/dsmr-reader/issues/3>`_)
- Updates ChartJS library tot 1.1, disposing django-chartjs plugin. Labels finally work! (as result of `#3 <https://github.com/dennissiemensma/dsmr-reader/issues/3>`_)
- Added trends page. (as result of `#3 <https://github.com/dennissiemensma/dsmr-reader/issues/3>`_)

- Recent history setting: set range (`#29 <https://github.com/dennissiemensma/dsmr-reader/issues/29>`_).
- Mock required for test: dsmr_weather.test_weather_tracking (`#32 <https://github.com/dennissiemensma/dsmr-reader/issues/32>`_).

- Massive refactoring: Separating apps & using signals (`#19 <https://github.com/dennissiemensma/dsmr-reader/issues/19>`_).
- README update: Exit character for cu (`#27 <https://github.com/dennissiemensma/dsmr-reader/issues/27>`_, by Jeroen Peters).
- Fixed untranslated strings in admin interface.
- Upgraded Django to 1.8.9.
