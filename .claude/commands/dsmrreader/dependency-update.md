Update all Python dependencies and the vendored web libraries:

```bash
cd /app/src && uv lock --upgrade && python scripts/sync_poetry_lock.py && poetry install --no-root
```

This re-resolves with uv (fast, low-memory), regenerates `poetry.lock` from the result, then syncs the venv.
It never invokes Poetry's own resolver, which is what used to run out of memory on updates. Poetry itself is
only ever used to install/run (`poetry install`, `poetry run ...`), never to resolve or lock.

The `poetry install --no-root` step is required: without it the venv stays on old versions, so formatters
like djlint run with the wrong version and produce output that fails CI's `--check` pass.

Report which packages were updated (`git diff uv.lock` or `git diff poetry.lock` for the version bumps).

Then update the vendored web libraries in `src/dsmr_frontend/static/dsmr_frontend/` (no package manager is used):

- Check each library against its latest release within the major version it is on (jQuery, Apache ECharts, Day.js, Flatpickr,
  Font Awesome). Skip new major versions and Bootstrap (see `TECH-DEBT.md`).
- Font Awesome is vendored as a versioned folder (`fontawesome-free-<version>-web`): replace the folder and update its path in
  `dsmr_frontend/templates/dsmr_frontend/base.html`. Other libraries are single files, replaced in place.
- Report which libraries were updated.

In the changelog (`documentation/docs/reference/changelog.md`) never list individual packages, libraries or versions. Add only the
generic line `- Package and web library updates` under `#### Miscellaneous` of the release being prepared.
