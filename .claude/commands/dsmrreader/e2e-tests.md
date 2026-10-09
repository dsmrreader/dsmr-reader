Run the Playwright browser (end-to-end) tests:

```bash
DJANGO_SETTINGS_MODULE=dsmrreader.config.test poetry run pytest -m e2e dsmr_frontend/tests/e2e --no-cov
```

These tests are excluded from the default `pytest` run and from CI. They need Chromium and its system libraries, which are installed in the development image.
If the browser fails to launch with `error while loading shared libraries`, the image is outdated: report that the development image must be rebuilt (`docker compose build dev-dsmr-app`) on the container host. Do not try to install system packages.

Report the test results.
