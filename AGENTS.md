# Agents directives

## Project assessment guidelines

When assessing a project, agents should consider the following criteria:
- Run Poetry updates: `docker compose exec dev-dsmr-app poetry update`
- Run Black: `docker compose exec dev-dsmr-app poetry run black .`
- Run Flake8: `docker compose exec dev-dsmr-app poetry run flake8 -v`
- Run MyPy: `docker compose exec dev-dsmr-app poetry run mypy .`
- Ensure code follows best practices and coding standards.

Caveats:
- The `src/` path in the project is mapped to `/app/` in the Docker container. Make sure to adjust paths accordingly when running commands inside the container.
- Tests to verify changes can be run with: ` docker compose exec -e DJANGO_SETTINGS_MODULE=dsmrreader.config.test -e DJANGO_DATABASE_HOST=tests-dsmr-db -e DJANGO_DATABASE_NAME=test_dsmrreader -e DJANGO_DATABASE_USER=testuser -e DJANGO_DATABASE_PASSWORD=testpasswd dev-dsmr-app poetry run pytest --cov --cov-report=html`
