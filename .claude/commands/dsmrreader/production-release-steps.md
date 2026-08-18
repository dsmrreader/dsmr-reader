Steps to follow when preparing a production release.

## 1. Sync the virtualenv with the lockfile
```bash
poetry install --no-root
```
Ensures the checkout runs the exact package versions from `poetry.lock`, not whatever happens to be installed. Do this before validation — an out-of-sync venv can pass checks locally using package versions that were never actually released.

## 2. Run validation
Run `/dsmrreader:quality-check` (format, template lint, type check, lint, lock sync, test). Stop and report if any step fails — do not proceed until it's clean.

## 3. Verify stable version
Check the `VERSION` tuple in `src/dsmrreader/__init__.py` (e.g. `VERSION = (6, 2, 0, "final", 0)`):
- Fourth element must be `"final"` (not `"beta"` or `"rc"`)
- Fifth element must be `0`

If either isn't met, update the tuple before proceeding. Report the verification status (PASS/FAIL).

## 4. Lock migrations
```bash
poetry run /app/src/manage.py dsmrreader_lock_migrations
```
This command writes the downgrade script to `provisioning/container/downgrade/v<version>.sh`.
Report the file path that was written and confirm the file exists.

## 5. Changelog
Entries must be short and non-technical. State what changed for the user, not how. No implementation details, no code references, no elaboration.

---
Once the release is out, run `/dsmrreader:new-development-release-start` to open the next development cycle.
