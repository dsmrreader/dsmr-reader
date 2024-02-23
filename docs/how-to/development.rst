Developing: Localhost
=====================


.. contents::
    :depth: 2


Setting up a development environment using Docker
-------------------------------------------------

.. note::

    I'm using JetBrain's PyCharm IDE for local development, which has builtin support for Git and Docker.
    Therefor some steps or information below may or may not match your own development stack.

- Install Docker on your system. E.g. Ubuntu: https://docs.docker.com/engine/install/ubuntu/ and consider rootless: https://docs.docker.com/engine/security/rootless/

- Clone DSMR-reader repository from GitHub::

    git clone ... (your fork)
    cd dsmr-reader/

- Symlink Docker files required (or just copy them)::

    # Either symlink
    ln -s dsmrreader/provisioning/container/Containerfile-dev Containerfile
    ln -s dsmrreader/provisioning/container/compose.dev.yml compose.yml

    # Or copy
    cp dsmrreader/provisioning/container/Containerfile-dev Containerfile
    cp dsmrreader/provisioning/container/compose.dev.yml compose.yml

- Copy Django settings template::

    cp dsmrreader/provisioning/django/settings.py.template dsmrreader/settings.py

- Open the settings template ``dsmrreader/settings.py`` you've copied and **replace**::

    from dsmrreader.config.production import *

- With::

    from dsmrreader.config.development import *

- Try running Docker (compose)::

    # This should build all the containers for local development
    docker-compose up -d

- Containers built? See if this command works::

    docker exec -it dsmr-app poetry run /app/manage.py check

    # Expected output: "System check identified no issues (0 silenced)"

- Now check whether tests run well in SQLite::

    ./tools/test-quick.sh

.. tip::

    Other DB engines can be tested as well, but the CI will take care of it anyway. The SQLite engine matches 99%% of the features DSMR-reader requires and it also runs in-memory, speeding up tests.

- When using PyCharm, you can add a new Interpreter using Docker Compose. Just select ``dsmr-app`` and set ``/opt/venv/bin/python`` as interpreter path. It should now map all dependencies used/installed in the container.


Initial data to develop with
----------------------------

To be honest, the best initial/fixture data is simply a backup of your own system in production.

.. danger::

    Please note that you should not run any (backend) processes in your DSMR-reader development environment, **until you've unlinked all external services**.

    After importing the backup of your production system, simply run::

        docker exec -it dsmr-app poetry run /app/manage.py development_reset

    This will remove all API keys and other links to externals systems, as well as reset the admin user credentials to ``admin / admin`` (user / password).

Just import it as you should on your RaspberryPi. Copy a database backup to ``/var/lib/postgresql/`` on your PC and import it::

    # NOTE: Some what broken when using Docker. But this was the legacy method:
    # Create empty database if it does not exist yet.
    sudo -u postgres createdb -O dsmrreader dsmrreader

    # For .SQL
    sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>
    
    # For .SQL.GZ
    zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo -u postgres psql dsmrreader


Fake datalogger
---------------

.. tip::

    There is a builtin command that can somewhat fake a datalogger::

        docker exec -it dsmr-app poetry run /app/manage.py dsmr_fake_datasource --with-gas --with-electricity-returned

It will generate random data every second in a certain pattern and should be fine for basic testing. 

Please note that it only inserts unprocessed readings, so you'll still have to run the following command to have the readings processed::

    docker exec -it dsmr-app poetry run /app/manage.py dsmr_backend --run-once


Running DSMR-reader locally
---------------------------

When running it with the default Docker compose config, the ``dsmr-app`` `Django Development Server application <https://docs.djangoproject.com/en/3.2/intro/tutorial01/#the-development-server>`_ will be accessible at: ``http://localhost:8000/``.

Any Python code changes you make will cause the Django Development Server to reload itself automatically.


Tests and coverage
------------------

DSMR-reader's test coverage should remain as high as possible, however this does not guarantee the quality of tests, so find a sweet spot for coverage whenever possible.

The easiest way to run tests is to use the SQLite (in-memory) tests::

    docker exec -it dsmr-app poetry run ./tools/quick-test.sh
    
To test a single app within DSMR-reader, just append it::

    docker exec -it dsmr-app poetry run ./tools/quick-test.sh dsmr_frontend

The test coverage should be visible in the terminal after running tests.
There are detailed HTML pages available as well, after each test run, in ``coverage_report/html/index.html``. 
Just open it with your browser to view the test coverage of each file and line.

.. note::

    A side effect of running tests is that it may also regenerate .PO files from the ``docs/`` folder. 
    If you did not make any changes there, your should just ignore those changed files and revert them.
    

Translations
------------

You can find the translations (.PO files) for the main application in ``dsmrreader/locales/``.
To regenerate them, just execute the ``docker exec -it dsmr-app poetry run ./tools/check-translations.sh`` script.


Editing documentation
---------------------

The documentation is part of the repository and can be generated (automatically) with Sphinx.

By default the Docker compose file should create and run a docs container for each language supported.

- English::

    http://127.0.0.1:10000

- Dutch::

    http://127.0.0.1:10001

Any changes you make will be reflected instantly in the browser, as Sphinx continuously checks for changed files.


Translating documentation
-------------------------

Translations are done using gettext and .PO files. Regenerate the .PO files with::

    docker exec -it dsmr-docs bash -c 'poetry run make gettext && poetry run sphinx-intl update --line-width=-1 -p _build/locale -l nl'

The .PO files in ``docs/locale`` should be regenerated now. You can use the open-source tool ``poedit`` to view and translate the files.
