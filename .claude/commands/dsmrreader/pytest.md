---
description: Run the full PyTest suite (the Playwright e2e tests are excluded, see /dsmrreader:e2e-tests).
---

Run the full PyTest test suite:

```bash
DJANGO_SETTINGS_MODULE=dsmrreader.config.test poetry run pytest -v
```

Report the test results.

