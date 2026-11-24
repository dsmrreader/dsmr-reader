---
description: Run the Playwright browser (end-to-end) tests. Excluded from the default pytest run and from CI.
---

Run the Playwright browser (end-to-end) tests from `/app/src`:

```bash
DJANGO_SETTINGS_MODULE=dsmrreader.config.test poetry run pytest -m e2e dsmr_frontend/tests/e2e --no-cov
```

These tests need Chromium and its system libraries. The system libraries are installed in the development image,
the browser binary is downloaded per Playwright version into the user cache.

Failure modes:
- `Executable doesn't exist at .../ms-playwright/...`: the browser build does not match the installed Playwright version
  (e.g. after a dependency update). Run `poetry run playwright install chromium` (user-cache download, no system packages) and rerun.
- `error while loading shared libraries`: the development image is outdated. Report that it must be rebuilt
  (`docker compose build dev-dsmr-app`) on the container host. Do not try to install system packages.

Report the test results (passed/failed counts).
