# DSMR-reader — Project Rules

## Project Overview

**DSMR-reader** is a Django / Python application for reading Dutch Smart Meter (DSMR P1 telegram) data and producing energy consumption statistics. 
It exposes a web UI, REST API, and integrates with external services (MQTT, InfluxDB, Dropbox, PVOutput, etc.).

---

## Tech Stack

| Concern               | Tool                                      |
|-----------------------|-------------------------------------------|
| Language              | Python                                    |
| Framework             | Django                                    |
| API                   | Django REST Framework                     |
| Dependency management | Poetry (`pyproject.toml` / `poetry.lock`) |
| Formatter             | Black (120-char line length)              |
| Template linter       | djlint                                    |
| Type checker          | MyPy                                      |
| Linter                | Flake8 + bandit                           |
| Tests                 | pytest + pytest-django + pytest-xdist     |
| DB (production)       | PostgreSQL (MySQL also supported)         |
| DB (development/test) | SQLite or env-configured                  |

---

## Repository Layout

```
/app/
├── dsmrreader/          # Django project package (settings, urls, wsgi, locales)
│   └── config/          # Settings: base, defaults, development, production, test
├── dsmr_api/            # REST API v1 & v2
├── dsmr_backend/        # Background processing & signal-based scheduling
├── dsmr_backup/         # DB backup services
├── dsmr_consumption/    # Consumption statistics generation
├── dsmr_datalogger/     # Core data reading & storage (DsmrReading model)
├── dsmr_dropbox/        # Dropbox integration
├── dsmr_frontend/       # Web UI (templates, static files, middleware)
├── dsmr_influxdb/       # InfluxDB export
├── dsmr_mindergas/      # Mindergas service
├── dsmr_mqtt/           # MQTT publishing
├── dsmr_notification/   # Email notifications
├── dsmr_parser/         # Bundled DSMR telegram parser (vendored from ndokter/dsmr_parser)
├── dsmr_plugins/        # Plugin system
├── dsmr_pvoutput/       # PVOutput service
├── dsmr_stats/          # Statistics aggregation
├── dsmr_weather/        # Weather data (Buienradar)
├── pyproject.toml
└── manage.py            # Defaults to production settings
```

---

## Code Conventions

### Formatting & Style
- **Line length**: 120 characters (Black + Flake8 both configured to 120).
- **Formatter**: Always run `poetry run black .` before committing.
- **Template linter**: Run `poetry run djlint --reformat .` for HTML templates.
- Do **not** manually wrap lines that Black will handle.

### Comments
- Comments must describe the current state, a fact, or a decision — never phrased relative to a change
  (no "now does X", "fixed to...", "changed from...", "used to be...", references to issues/PRs/tasks).
- Code and comments should read the same whether written today or found in the repo in five years.

### Type Hints
- All new code must include type hints compatible with MyPy strict mode.
- Third-party libraries without stubs are listed under `[[tool.mypy.overrides]]` in `pyproject.toml` with `ignore_missing_imports = true` — add new ones there as needed.

### Architecture Patterns
- **Service layer**: Business logic lives in `services.py`, not in models or views.
- **DTOs**: Use `dto.py` dataclasses for inter-app data transfer.
- **Signals**: Apps communicate via Django signals defined in `dsmr_backend/signals.py`. Register handlers with `@receiver`.
- **Singleton settings**: Use `django-solo` (`SoloAppConfig`) for per-app configuration models.
- **Custom QuerySet managers**: Use `.unprocessed()`, `.processed()`, etc. — follow existing patterns.
- **Mixins**: Use `ModelUpdateMixin`, `InfiniteManagementCommandMixin`, etc. from the existing mixin library.

### Tests
- Tests use **pytest** (not `unittest.TestCase` directly).
- Fixture files live in `<app>/fixtures/`.
- Test paths are declared in `pyproject.toml` — add new apps there.
- Run with: `poetry run pytest -v`
- Parallelisation via `pytest-xdist` is available (`-n auto`).

### Migrations
- Generate with: `poetry run /app/src/manage.py makemigrations`
- Apply with: `poetry run /app/src/manage.py migrate`
- Lock for release with `/dsmrreader:production-release-steps`
- **Never edit locked migrations.**

### Environment / Configuration
- Use `python-decouple` (`config()`) for all environment-variable access. Never hardcode secrets.
- Pattern for optional overrides:
  ```python
  try:
      SOME_SETTING = config("SOME_SETTING")
  except UndefinedValueError:
      pass
  ```
- Settings split by environment: `base.py` → `defaults.py` → `development.py` / `production.py` / `test.py`.

---

## Excluded Directories

Never modify, format, lint, or type-check these:
- `.venv/*`
- `*/migrations/*`
- `dsmr_plugins/modules/*`
- `dsmr_dropbox/dropboxinc/*`

`dsmr_parser/*` is a vendored fork of upstream `ndokter/dsmr_parser` — don't hand-edit its logic outside of
a deliberate upstream sync (see `value_types.py`, which is a deliberate DSMR-reader rewrite and must never
be overwritten from upstream). It IS covered by Black and MyPy like the rest of the codebase; only Flake8
excludes it (see `pyproject.toml`).

---

## Quality Pipeline (run in order)

```bash
poetry run black .                          # 1. Format Python
poetry run djlint --reformat .              # 2. Format templates
poetry run mypy /app/src                    # 3. Type check
poetry run flake8                           # 4. Lint
poetry run pytest -v                        # 5. Test
```

All steps must pass before a change is considered complete. **Always run `/dsmrreader:quality-check` after making any code changes.**

Steps 1-4 (Black, djlint, MyPy, Flake8 — not the test suite) also run automatically as git pre-commit hooks via
the `pre-commit` framework (`.pre-commit-config.yaml` at the repo root). Run `poetry run pre-commit install`
once per checkout to enable them; a commit is blocked/auto-fixed if any of them fail.

---

## Django Settings

- Default settings module (via `manage.py`): `dsmrreader.config.production`
- Test settings module: `dsmrreader.config.test` (configured in `pyproject.toml`)
- Development: set `DJANGO_SETTINGS_MODULE=dsmrreader.config.development`

---

## API

- **v1**: Legacy — avoid adding new endpoints here.
- **v2**: Active — DRF with `LimitOffsetPagination` (25/page), `OrderingFilter`, `DjangoFilterBackend`.
- Authentication: custom `HeaderAuthentication` via `X-AUTHKEY` or `Authorization: Token <key>` headers.

---

## i18n

- Default language: English (`en`). Supported: Dutch (`nl`) and English (`en`).
- Translation files: `/app/dsmrreader/locales/`.
- Use `gettext_lazy` (`_()`) for all user-visible strings.
