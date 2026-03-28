# Hall of Fame & Credits

## Author

DSMR-reader was originally authored by [Dennis Siemensma](https://www.linkedin.com/in/dennissiemensma) and started in **2015**.

## Special thanks

For providing their time and support:

- [Bram van Dartel](https://www.linkedin.com/in/bramvandartel/) ([@xirixiz](https://github.com/xirixiz)) — author of [DSMR-reader Docker](https://github.com/xirixiz/dsmr-reader-docker) and providing the containers
- [Nigel Dokter](https://www.linkedin.com/in/nigel-dokter-5321ab110/) ([@ndokter](https://github.com/ndokter)) — author of [DSMR-parser](https://github.com/ndokter/dsmr_parser)
- [Jeroen Peters](https://www.linkedin.com/in/jeroen-peters-nl/) ([@jeroenpeters1986](https://github.com/jeroenpeters1986))
- [JetBrains](https://www.jetbrains.com/?from=DSMR-reader) — for providing a JetBrains IDE license to work on DSMR-reader for many years
- [All contributors on GitHub](https://github.com/dsmrreader/dsmr-reader/graphs/contributors)


## Other thanks to

- [GitHub](https://github.com/) for hosting the project code and issues
- [Read The Docs](https://readthedocs.org/) for hosting all documentation of DSMR-reader


## Software used

DSMR-reader would **not have been possible** without the following software and projects:

### Language & framework

- [Python](https://www.python.org/) — the language powering DSMR-reader
- [Django](https://www.djangoproject.com/) — web framework
- [Django REST Framework](https://www.django-rest-framework.org) — REST API layer
- [gunicorn](https://gunicorn.org/) — WSGI HTTP server
- [PostgreSQL](https://www.postgresql.org/) — production database
- [psycopg2](https://www.psycopg.org/) — PostgreSQL adapter

### Django extensions

- [django-solo](https://github.com/lazybird/django-solo) — singleton settings models
- [django-filter](https://django-filter.readthedocs.io/) — queryset filtering for the API
- [django-mathfilters](https://github.com/dbrgn/django-mathfilters) — template math filters
- [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) — color picker for admin
- [django-admin-rangefilter](https://github.com/silentsokolov/django-admin-rangefilter) — date range filter in admin
- [django-admin-sortable](https://github.com/jrief/django-admin-sortable2) — sortable admin lists
- [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/) — development debugging panel

### Integrations & protocols

- [paho-mqtt](https://github.com/eclipse/paho.mqtt.python) — MQTT client
- [influxdb-client](https://github.com/influxdata/influxdb-client-python) — InfluxDB integration
- [dropbox](https://github.com/dropbox/dropbox-sdk-python) — Dropbox SDK
- [pyserial](https://github.com/pyserial/pyserial) — serial port communication
- [pyserial-asyncio](https://github.com/pyserial/pyserial-asyncio) — async serial port support
- [Buienradar](https://www.buienradar.nl) — Dutch weather data provider

### Utilities

- [python-decouple](https://github.com/HBNetwork/python-decouple) — environment-based configuration
- [python-dateutil](https://dateutil.readthedocs.io/) — date parsing utilities
- [requests](https://requests.readthedocs.io/) — HTTP client
- [pyyaml](https://pyyaml.org/) — YAML parsing
- [attrs](https://www.attrs.org/) — data classes
- [crcmod](https://crcmod.sourceforge.net/) — CRC checksum for P1 telegram validation
- [packaging](https://packaging.pypa.io/) — version parsing utilities
- [uritemplate](https://uritemplate.readthedocs.io/) — URI template expansion

### Frontend

- [Bootstrap](https://getbootstrap.com/) — CSS framework
- [jQuery](https://jquery.com/) — JavaScript utility library
- [Apache ECharts](https://echarts.apache.org/) — interactive charts and graphs
- [Day.js](https://day.js.org/) — lightweight date/time library
- [Flatpickr](https://flatpickr.js.org/) — date picker widget
- [Font Awesome](https://fontawesome.com/) — icon set
- [Director Responsive Admin](https://github.com/nichealpham/director-responsive-admin) — admin UI template <small>*(original website offline)*</small>
- [ReDoc](https://github.com/Redocly/redoc) — API documentation renderer
- Favicon made by [Freepik](https://www.freepik.com/) from [flaticon.com](https://www.flaticon.com/free-icon/eco-energy_25013)
- [Real Favicon Generator](https://realfavicongenerator.net) — favicon tooling

### Documentation

- [MkDocs](https://www.mkdocs.org/) — static site generator for documentation
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) — documentation theme
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/) — Markdown extensions (admonitions, code highlighting, superfences, tabs)
- [Read The Docs](https://readthedocs.org/) — documentation hosting

### Development tools

- [Poetry](https://python-poetry.org/) — dependency management and packaging
- [Black](https://black.readthedocs.io/) — Python code formatter
- [Flake8](https://flake8.pycqa.org/) — Python linter (with bandit and bugbear plugins)
- [MyPy](https://mypy.readthedocs.io/) — static type checker
- [djlint](https://www.djlint.com/) — Django template linter and formatter
- [pytest](https://pytest.org/) — test framework (with pytest-django and pytest-xdist)
- [Claude Code](https://claude.ai/code) by [Anthropic](https://www.anthropic.com/) — AI coding assistant

---

## Previously used software

Software that was part of DSMR-reader in earlier versions but has since been removed or replaced:

### Frontend (removed)

- [Bootstrap Datepicker](https://bootstrap-datepicker.readthedocs.org/) — date picker widget *(replaced by Flatpickr)*
- [Moment.js](https://momentjs.com/) — date/time library *(replaced by Day.js)*
- [Semantic UI](https://semantic-ui.com/) — UI component framework *(search component replaced by plain jQuery)*
- [iCheck](https://github.com/fronteed/icheck) — custom checkbox and radio inputs *(removed, unused)*
- [jQuery Inputmask](https://github.com/RobinHerbots/Inputmask) — input masking plugin *(removed, unused)*
- [jQuery placeholder](https://github.com/mathiasbynens/jquery-placeholder) — placeholder polyfill *(removed, unused)*
- [jQuery slimScroll](https://github.com/rochal/jQuery-slimScroll) — custom scrollbar plugin *(removed, unused)*
- [jQuery ba-resize](https://github.com/cowboy/jquery-resize) — element resize event plugin *(removed, replaced by ResizeObserver)*
- [Ionicons](https://ionic.io/ionicons) — icon set *(removed, unused)*
- [html5shiv](https://github.com/aFarkas/html5shiv) — HTML5 compatibility for older browsers *(removed)*
- [Respond.js](https://github.com/scottjehl/Respond) — CSS media query polyfill for IE *(removed)*
