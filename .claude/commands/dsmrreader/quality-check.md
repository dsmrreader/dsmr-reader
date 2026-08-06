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
poetry run mypy /app/src
```

4. **Lint Python** (Flake8):
```bash
poetry run flake8 -v
```

5. **Check pyproject.toml/uv.lock/poetry.lock are all in sync**:
```bash
uv lock --check && python scripts/sync_poetry_lock.py && git diff --exit-code poetry.lock && poetry check
```
If `uv lock --check` fails, pyproject.toml changed and uv.lock is stale — run `uv lock` and commit it. If `git diff --exit-code` fails, poetry.lock was stale and has now been regenerated from uv.lock — stage it. If `poetry check` fails, pyproject.toml and poetry.lock disagree.

6. **Test** (PyTest):
```bash
DJANGO_SETTINGS_MODULE=dsmrreader.config.test poetry run pytest -v
```

Report results for each step. Stop and report if any step fails.

