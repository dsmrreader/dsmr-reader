# Agents directives

## Project assessment guidelines

When assessing a project, agents should consider the following criteria:
- Run Poetry updates: `docker compose exec dev-dsmr-app poetry update`
- Run Black: `docker compose exec dev-dsmr-app poetry run black .`
- Run Flake8: `docker compose exec dev-dsmr-app poetry run flake8 -v`
- Run MyPy: `docker compose exec dev-dsmr-app poetry run mypy .`
- Ensure code follows best practices and coding standards.
