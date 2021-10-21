Developing: Localhost
=====================


.. contents::
    :depth: 2


Setting up a development environment using Docker
-------------------------------------------------

Install Docker on your system.

Clone DSMR-reader repository from GitHub::

    git clone ... (your fork)
    cd dsmr-reader/

Symlink files required::

    ln -s dsmrreader/provisioning/docker/Dockerfile-dev Dockerfile
    ln -s dsmrreader/provisioning/docker/docker-compose.dev.yml docker-compose.yml

Copy development config::

    cp dsmrreader/provisioning/django/settings.py.template dsmrreader/settings.py

Open ``dsmrreader/settings.py`` and replace::

    from dsmrreader.config.production import *

With::

    from dsmrreader.config.development import *

Try running Docker and see if this command works, output should be something like ``System check identified no issues (0 silenced).``::
    
    docker exec -it dsmr-app poetry run /app/manage.py check

Set up MySQL (or MariaDB) test database::

    # NOTE: Some what broken when using Docker. But this was the legacy method:
    mysql_tzinfo_to_sql /usr/share/zoneinfo | sudo mysql --defaults-file=/etc/mysql/debian.cnf mysql
    sudo mysql --defaults-file=/etc/mysql/debian.cnf

Now check whether tests run well with all three database backends (this may take a while)::

    ./tools/test-all.sh


Initial data to develop with
----------------------------

To be honest, the best initial/fixture data is simply a backup of your own system in production.

Just import it as you should on your RaspberryPi. Copy a database backup to ``/var/lib/postgresql/`` on your PC and import it::

    # NOTE: Some what broken when using Docker. But this was the legacy method:
    # Create empty database if it does not exist yet.
    sudo -u postgres createdb -O dsmrreader dsmrreader

    # For .SQL
    sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>
    
    # For .SQL.GZ
    zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo -u postgres psql dsmrreader

.. danger::
    
    Please note that you should not run any (backend) processes in your DSMR-reader development environment, until you've unlinked all external services.

    After importing the backup of your production system, simply run::
    
        docker exec -it dsmr-app poetry run /app/manage.py development_reset

    This will remove all API keys and other links to externals systems, as well as reset the admin user credentials to ``admin / admin`` (user / password). 


Fake datalogger
---------------

There is a builtin command that can somewhat fake a datalogger::
    
    docker exec -it dsmr-app poetry run /app/manage.py dsmr_fake_datasource --with-gas --with-electricity-returned

It will generate random data every second in a certain pattern and should be fine for basic testing. 

Please note that it only inserts unprocessed readings, so you'll still have to run the following command to have the readings processed::

    docker exec -it dsmr-app poetry run /app/manage.py dsmr_backend --run-once


Running DSMR-reader locally
---------------------------

You can run the Django development server with::

    docker exec -it dsmr-app poetry run /app/manage.py runserver

The application will be accessible on: ``http://localhost:8000/``.
Any code changes you make will let the application reload automatically.


Tests and coverage
------------------

DSMR-reader's test coverage should remain as high as possible. Running tests will also analyze the test coverage in detail. 

The easiest way to run tests is to use the in-memory tests::

    docker exec -it dsmr-app poetry run ./tools/quick-test.sh
    
To test a single app within DSMR-reader, just append it::

    docker exec -it dsmr-app poetry run ./tools/quick-test.sh dsmr_frontend

To test all database backends, run::

    docker exec -it dsmr-app poetry run ./tools/test-all.sh

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

The documentation is part of the repository and can be generated (automatically) with Sphinx::

    docker exec -it dsmr-docs poetry run sphinx-autobuild . _build/html --host 0.0.0.0 --port 10000
    
You can now view the documentation in your browser by accessing: ``http://127.0.0.1:10000``.
Any changes you make will be reflected instantly in the browser, as Sphinx continuously checks for changed files.


Translating documentation
-------------------------

Translations are done using gettext and .PO files. Regenerate the .PO files with::

    docker exec -it dsmr-docs bash -c 'poetry run make gettext && poetry run sphinx-intl update --line-width=-1 -p _build/locale -l nl'

The .PO files in ``docs/locale`` should be regenerated now. You can use ``poedit`` to view and translate the files.

After editing the .PO files, you can check the result by building the Dutch translations locally::

    docker exec -it dsmr-docs poetry run make html

Now view the generated HTML in your browser by opening: ``docs/_build/html/index.html``
