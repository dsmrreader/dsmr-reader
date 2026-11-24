---
description: Type check the project with MyPy (strict). Always invoked with the absolute path /app/src.
---

Run MyPy type checker on the project, from `/app/src` and with the absolute path (matches CI, other forms give wrong results):

```bash
cd /app/src && poetry run mypy /app/src
```

Report any type errors found.

