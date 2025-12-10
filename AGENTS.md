# Agents directives

## General guidelines
- The `src/` path in the project is mapped to `/app/` in the Docker container. Make sure to adjust paths accordingly when running commands inside the container, such as MyPy.
- Run Black, MyPy and tests to verify changes after making modifications.
- Temporary files and reports must be placed in `.agent-data/` to prevent them from being committed.
- Delete temporary files created for command output.
- If the docker container for running commands is not available, pause and inform the user to manually fix it.


## Project integrity guidelines
- Run Poetry updates: `docker compose exec dev-dsmr-app poetry update`
- Run Black: `docker compose exec dev-dsmr-app poetry run black .`
- Run djLint: `docker compose exec dev-dsmr-app poetry run djlint --reformat .`
- Run Flake8: `docker compose exec dev-dsmr-app poetry run flake8 -v`
- Run MyPy: `docker compose exec dev-dsmr-app poetry run mypy /app`
- Run Tests: `docker compose exec -e DJANGO_SETTINGS_MODULE=dsmrreader.config.test dev-dsmr-app poetry run pytest -q`


## Project assessment guidelines
- Run the "Project state guidelines" mentioned above.
- Ensure code follows best practices and coding standards.
- Suggest commonly used tools for code quality and consistency.
- Check documentation for typos and errors. It resides in the `documentation` folder.
- In `pyproject.toml` the `[tool.poetry.dependencies]` and `[tool.poetry.group.dev.dependencies]` sections should have all packages sorted alphabetically.
