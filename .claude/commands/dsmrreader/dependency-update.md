Update all Python dependencies:

```bash
cd /app/src && uv lock --upgrade && python scripts/sync_poetry_lock.py && poetry install --no-root
```

This re-resolves with uv (fast, low-memory), regenerates `poetry.lock` from the result, then syncs the venv.
It never invokes Poetry's own resolver, which is what used to run out of memory on updates. Poetry itself is
only ever used to install/run (`poetry install`, `poetry run ...`), never to resolve or lock.

The `poetry install --no-root` step is required: without it the venv stays on old versions, so formatters
like djlint run with the wrong version and produce output that fails CI's `--check` pass.

Report which packages were updated (`git diff uv.lock` or `git diff poetry.lock` for the version bumps).
