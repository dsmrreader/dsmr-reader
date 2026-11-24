# DSMR-reader — Project Rules

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

## Container Image Build (before commit and push)

The development image installs the locked Playwright version and its OS dependencies
(`provisioning/container/Containerfile-dev`), so a dependency or image change can break the image build
even when every step of the quality pipeline passes.

**Before committing or pushing** a change to any of these, the image must build successfully:
- `pyproject.toml`, `uv.lock` or `poetry.lock` (including `/dsmrreader:dependency-update`)
- anything under `provisioning/container/`
- `compose.yml` / `compose.override.yml`

```bash
docker compose build dev-dsmr-app
```

- Run it when a container runtime is available. If it fails, stop and report the failing step — do not commit or push.
- When no container runtime is available (`docker` missing in the agent environment), the check cannot be skipped:
  ask the user to run the build on the container host and wait for their confirmation before committing or pushing.
- Never mark such a change as done on the strength of the quality pipeline alone.

---

## Git Commit Messages

Single line, no body. `<type>: <short summary>`, optionally referencing an issue number. No multi-paragraph
explanations of what/why — that belongs in the PR description, not the commit.

---

## Django Settings

- Default settings module (via `manage.py`): `dsmrreader.config.production`
- Test settings module: `dsmrreader.config.test` (configured in `pyproject.toml`)
- Development: set `DJANGO_SETTINGS_MODULE=dsmrreader.config.development`

---

## API

- **v1** is legacy: do not add new endpoints there. New work goes in **v2**.

---

## i18n

- Default language: English (`en`). Supported: Dutch (`nl`) and English (`en`).
- Translation files: `/app/dsmrreader/locales/`.
- Use `gettext_lazy` (`_()`) for all user-visible strings.
