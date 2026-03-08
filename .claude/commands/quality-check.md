Run the full quality verification pipeline. Execute all steps in order and report results:

1. **Format** (Black):
```bash
poetry run black .
```

2. **Lint HTML** (djlint):
```bash
poetry run djlint --reformat .
```

3. **Type check** (MyPy):
```bash
poetry run mypy /app
```

4. **Lint Python** (Flake8):
```bash
poetry run flake8 -v
```

5. **Test** (PyTest):
```bash
DJANGO_SETTINGS_MODULE=dsmrreader.config.test poetry run pytest -q
```

Report results for each step. Stop and report if any step fails.

