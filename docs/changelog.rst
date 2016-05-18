Changelog
=========


v1.2.0 - 2016-xx-xx
^^^^^^^^^^^^^^^^^^^
- Energy supplier prices does not indicate tariff type (Django admin) (`#126 <https://github.com/dennissiemensma/dsmr-reader/issues/126>`_).
- Requirements update (`#128 <https://github.com/dennissiemensma/dsmr-reader/issues/128>`_).
- Force backup (`#123 <https://github.com/dennissiemensma/dsmr-reader/issues/123>`_).
- Update clean-install.md (`#131 <https://github.com/dennissiemensma/dsmr-reader/issues/131>`_).
- Improve data export field names (`#132 <https://github.com/dennissiemensma/dsmr-reader/issues/132>`_).
- Display average temperature in archive (`#122 <https://github.com/dennissiemensma/dsmr-reader/issues/122>`_).
- Pie charts on trends page overlap their canvas (`#136 <https://github.com/dennissiemensma/dsmr-reader/issues/136>`_).
- 'Slumber' consumption (`#115 <https://github.com/dennissiemensma/dsmr-reader/issues/115>`_).
- Show lowest & highest Watt peaks (`#138 <https://github.com/dennissiemensma/dsmr-reader/issues/138>`_).
- Reset day & hour statistics when changing energy prices (`#95 <https://github.com/dennissiemensma/dsmr-reader/issues/95>`_).


v1.1.2 - 2016-05-01
^^^^^^^^^^^^^^^^^^^
- Trends page giving errors (when lacking data) (`#125 <https://github.com/dennissiemensma/dsmr-reader/issues/125>`_).


v1.1.1 - 2016-04-27
^^^^^^^^^^^^^^^^^^^
- Improve readme (`#124 <https://github.com/dennissiemensma/dsmr-reader/issues/124>`_).


v1.1.0 - 2016-04-23
^^^^^^^^^^^^^^^^^^^
- Autorefresh dashboard (`#117 <https://github.com/dennissiemensma/dsmr-reader/issues/117>`_).
- Improve line graphs' visibility (`#111 <https://github.com/dennissiemensma/dsmr-reader/issues/111>`_).
- Easily add notes (`#110 <https://github.com/dennissiemensma/dsmr-reader/issues/110>`_).
- Export data points in CSV format (`#2 <https://github.com/dennissiemensma/dsmr-reader/issues/2>`_).
- Allow day/month/year comparison (`#94 <https://github.com/dennissiemensma/dsmr-reader/issues/94>`_).
- Docs: Add FAQ and generic application info (`#113 <https://github.com/dennissiemensma/dsmr-reader/issues/113>`_).
- Support for Iskra meter (DSMR 2.x) (`#120 <https://github.com/dennissiemensma/dsmr-reader/issues/120>`_).


v1.0.1 - 2016-04-07
^^^^^^^^^^^^^^^^^^^
- Update licence to OSI compatible one (`#119 <https://github.com/dennissiemensma/dsmr-reader/issues/119>`_).


v1.0.0 - 2016-04-07
^^^^^^^^^^^^^^^^^^^
- First official stable release.


[β] v0.1 (2015-10-29) to 0.16 (2016-04-06)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All previous beta releases/changes have been combined to a single list below:

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
