Update all Python dependencies:

```bash
cd /app/src && uv lock --upgrade && python scripts/sync_poetry_lock.py
```

This re-resolves with uv (fast, low-memory) and regenerates `poetry.lock` from the result — it never invokes
Poetry's own resolver, which is what used to run out of memory on updates. Poetry itself is only ever used to
install/run (`poetry install`, `poetry run ...`), never to resolve or lock.

Report which packages were updated (`git diff uv.lock` or `git diff poetry.lock` for the version bumps).
