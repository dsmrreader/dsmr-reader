# Agent Directives

## Environment Setup
- **Container paths**: `src/` maps to `/app/` in Docker. Use `/app/` for container commands (MyPy, linting, tests).
- **Container unavailable**: If Docker container is unreachable, pause and request manual intervention from user.

## After Code Changes: Quality Verification
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
