# Developing

## Setting up a development environment using Docker

!!! note

    I'm using JetBrain's PyCharm IDE for local development, which has builtin support for Git and Docker.
    Therefor some steps or information below may or may not match your own development stack.

- Install Docker on your system. E.g. [how-to for Ubuntu](https://docs.docker.com/engine/install/ubuntu/) and consider [Docker rootless](https://docs.docker.com/engine/security/rootless/).

- Clone DSMR-reader repository from GitHub:

```shell title="shell"
    git clone <link to your fork>
    cd dsmr-reader/
```

- Symlink Compose/ev files required (or just copy them):

```shell title="shell"
    # Either symlink
    ln -s provisioning/container/compose.dev.yml compose.yml
    ln -s provisioning/container/dev.env compose.env

    # Or copy
    cp provisioning/container/compose.dev.yml compose.yml
    cp provisioning/container/dev.env compose.env
```

- Try running Docker (compose):

```shell title="shell"
    # This should build all the containers for local development
    docker-compose up -d
```

- Containers built? See if this command works:

```shell title="shell"
    docker exec -it dev-dsmr-app poetry run /app/src/manage.py check

    # Expected output: "System check identified no issues (0 silenced)"
```


- When using PyCharm, you can add a new Interpreter using Docker Compose. Just select ``dev-dsmr-app`` and set ``/opt/venv/bin/python`` as interpreter path. It should now map all dependencies used/installed in the container.


## Running DSMR-reader locally

When running it with the default Docker compose config, the Django Development Server application will be accessible at:

[http://localhost:8000](http://localhost:8000/){ .md-button }

Any Python code changes you make will cause the Django Development Server to reload itself automatically.

## Translations

- Update the code and add translatable strings.
- Run ``makemessages`` to extract those strings:

```shell title="shell"
docker compose exec dev-dsmr-app poetry run /app/src/manage.py makemessages -l nl
```
 
- Open ``dsmr_frontend/locale/en/LC_MESSAGES/django.po`` with PO Editor or a similar tool and translate the new strings.
- After translation, run ``compilemessages`` to compile the PO-translations into the MO-files:

```shell title="shell"
docker compose exec dev-dsmr-app poetry run /app/src/manage.py compilemessage
```

## Code style
```shell title="shell"
docker compose exec dev-dsmr-app poetry run black .
docker compose exec dev-dsmr-app poetry run flake8 -v
```

## Managing dependencies

Dependencies are declared in `src/pyproject.toml` (`[project.dependencies]` for runtime, `[dependency-groups.dev]` for development/test tooling).
Poetry remains the tool actually used to install and run everything (`poetry install`, `poetry run ...`, in containers and CI), but resolving/locking is done with [uv](https://docs.astral.sh/uv/) instead of Poetry's own resolver, since Poetry's resolver can run out of memory when a constraint change forces it to backtrack over a large version range.

To add, remove or update a dependency:

```shell title="shell"
uv add some-package               # or: uv remove some-package
uv lock                           # re-resolve and refresh uv.lock
python scripts/sync_poetry_lock.py  # regenerate poetry.lock from uv.lock
poetry check                      # optional: confirm Poetry accepts the result
```

`scripts/sync_poetry_lock.py` writes `poetry.lock` directly from `uv.lock` and never invokes Poetry's resolver, so it's the same low-memory operation regardless of how large the dependency graph gets.
Commit both `uv.lock` and the regenerated `poetry.lock`.

## Tests
```shell title="shell"
docker compose exec -e DJANGO_SETTINGS_MODULE=dsmrreader.config.test dev-dsmr-app poetry run pytest
```

The `-e DJANGO_SETTINGS_MODULE=dsmrreader.config.test` part is important, as some tests may fail otherwise.

## Other stuff
There is some more to it, such as tests and documentation. If you ever need to work on those, just see how similar stuff works in the project. Or ask for more information.
