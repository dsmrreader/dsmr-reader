# Developing

## Setting up a development environment using Docker

!!! note

    I'm using JetBrain's PyCharm IDE for local development, which has builtin support for Git and Docker.
    Therefor some steps or information below may or may not match your own development stack.

- Install Docker on your system. E.g. [how-to for Ubuntu](https://docs.docker.com/engine/install/ubuntu/) and consider [Docker rootless](https://docs.docker.com/engine/security/rootless/).

- Clone DSMR-reader repository from GitHub:

```shell
    git clone <link to your fork>
    cd dsmr-reader/
```

- Symlink Docker files required (or just copy them):

```shell
    # Either symlink
    ln -s provisioning/container/compose.dev.yml compose.yml

    # Or copy
    cp provisioning/container/compose.dev.yml compose.yml
```

- Try running Docker (compose):

```shell
    # This should build all the containers for local development
    docker-compose up -d
```

- Containers built? See if this command works:

```shell
    docker exec -it dev-dsmr-app poetry run /app/manage.py check

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

```shell
docker compose exec dev-dsmr-app poetry run /app/manage.py makemessages -l nl
```
 
- Open ``dsmr_frontend/locale/nl/LC_MESSAGES/django.po`` with PO Editor or a similar tool and translate the new strings.
- After translation, run ``compilemessages`` to compile the PO-translations into the MO-files:

```shell
docker compose exec dev-dsmr-app poetry run /app/manage.py compilemessage
```

## Code style
```shell
docker compose exec dev-dsmr-app poetry run black .
docker compose exec dev-dsmr-app poetry run flake8 -v
```

## Other stuff
There is some more to it, such as tests and documentation. If you ever need to work on those, just see how similar stuff works in the project. Or ask for more information.
