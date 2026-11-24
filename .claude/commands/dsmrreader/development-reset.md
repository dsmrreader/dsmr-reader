---
description: Reset the development database and data to a clean state. Destructive, only on request.
disable-model-invocation: true
---

Reset the development environment to a clean state. This wipes development data, so confirm with the user first:

```bash
poetry run /app/src/manage.py development_reset
```

Report the result.

