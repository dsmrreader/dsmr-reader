# Agent Directives

## Development
- **Container paths**: `src/` maps to `/app/` in Docker. Use `/app/` for container commands (MyPy, linting, tests).
- **Container unavailable**: If Docker container is unreachable, do not debug but request manual intervention from user.
- **CLI**: Prevent your CLI commands and their output from being stored in the local user's bash history.

## After Code Changes: Quality Verification
- **Test paths**: `src/` maps to `/app/` in Docker. Use `/app/` for container commands (MyPy, linting, tests).
- **Test optimization**: Run a single test first to ensure nothing big is broken.
- **Test output**: Never use pipes to see testing output, it does not work.

Always run these in order:
1. **Format**: `docker compose exec dev-dsmr-app poetry run black .`
2. **Lint HTML**: `docker compose exec dev-dsmr-app poetry run djlint --reformat .`
3. **Type check**: `docker compose exec dev-dsmr-app poetry run mypy /app`
4. **Lint Python**: `docker compose exec dev-dsmr-app poetry run flake8 -v`
5. **Test**: `docker compose exec -e DJANGO_SETTINGS_MODULE=dsmrreader.config.test dev-dsmr-app poetry run pytest -q`

## Maintenance Tasks
- **Update dependencies**: `docker compose exec dev-dsmr-app poetry update`
- **Sort packages**: In `pyproject.toml`, keep `[tool.poetry.dependencies]` and `[tool.poetry.group.dev.dependencies]` alphabetically sorted.
- **Clean up**: Remove temporary files; store reports in `.agent-data/` to prevent commits.

## Code Quality Standards
- Follow best practices and Django conventions.
- Ensure code consistency across the project.
- Check `documentation/` folder for typos and clarity.
- Run all quality checks (above) before considering work complete.
- Imports should always reside at the top of the file.

## Release Steps
### Verify Stable Version
Verify that the version in `dsmrreader/__init__.py` is configured for a stable release.

**Requirements**:
- Fourth element must be: `"final"` (indicates stable release)
- Last element must be: `0` (indicates first release of that version)
- Example: `VERSION = (6, 0, 0, "final", 0)` ✅

**Process**:
1. Check `src/dsmrreader/__init__.py` for the `VERSION` tuple
2. Verify fourth element is `"final"` (not "beta" or "rc")
3. Verify last element is `0`
4. If requirements are not met, update the version tuple before proceeding with release
5. Report the verification status (PASS/FAIL) before continuing to Lock Migrations step

### Lock Migrations
Execute the following command to lock migrations for a new release:
```bash
docker compose exec dev-dsmr-app poetry run /app/manage.py dsmrreader_lock_migrations
```

**Process**:
1. The command outputs a file name (e.g., `provisioning/downgrade/v6.0.0.sh`)
2. Extract the file name from the output
3. The output also contains the bash script content (migration commands)
4. Create the file with the provided path and write the bash script content to it
5. Ensure the file has executable permissions: `chmod +x provisioning/downgrade/v<VERSION>.sh`
