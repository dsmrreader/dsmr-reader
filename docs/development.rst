Developing with DSMR-reader
===========================


.. contents::
    :depth: 2

.. note::

    In this document there are many references to::
    
        source ~/.virtualenvs/dsmrreader/bin/activate
        
    You will only have to execute it once per terminal session, to make sure you are working in the designated virtual env for DSMR-reader.


Setting up a development environment in Ubuntu 18.04
----------------------------------------------------

System packages::
    
    sudo apt-get install -y postgresql postgresql-server-dev-all git python3 python3-pip python3-virtualenv virtualenvwrapper libmysqlclient-dev mariadb-server poedit

Clone DSMR-reader repository from Github::

    git clone ... (your fork)
    cd dsmr-reader/

Create virtualenv and install all packages::

    mkdir ~/.virtualenvs
    virtualenv ~/.virtualenvs/dsmrreader --no-site-packages --python python3
    source ~/.virtualenvs/dsmrreader/bin/activate
    pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/dev.txt

Copy development config::

    cp dsmrreader/provisioning/django/development.py dsmrreader/settings.py

Try a check, output should be something like ``System check identified no issues (0 silenced).``::
    
    ./manage.py check

Run quick tests (with in-memory database)::

    ./tools/quick-test.sh

Set up PostgreSQL test database::

    sudo sudo -u postgres createuser -DSR dsmrreader
    sudo sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"
    sudo sudo -u postgres psql -c "alter user dsmrreader CREATEDB;"

Set up MySQL (or MariaDB) test database::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | sudo mysql --defaults-file=/etc/mysql/debian.cnf mysql
    sudo mysql --defaults-file=/etc/mysql/debian.cnf

    # Execute these queries:
    GRANT ALL PRIVILEGES ON *.* TO 'dsmrreader'@'localhost' IDENTIFIED BY 'dsmrreader';
    FLUSH PRIVILEGES;

Now check whether tests run well with all three database backends (this may take a while)::

    ./tools/test-all.sh


Initial data to develop with
----------------------------

To be honest, the best initial/fixture data is simply a backup of your own system in production.

Just import it as you should on your RaspberryPi. Copy a database backup to ``/var/lib/postgresql/`` on your PC and import it::

    # Create empty database if it does not exist yet.
    sudo sudo -u postgres createdb -O dsmrreader dsmrreader

    # For .SQL
    sudo sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>
    
    # For .SQL.GZ
    zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo sudo -u postgres psql dsmrreader

.. warning::
    
    Please note that you should not run any (backend) processes in your DSMR-reader development environment, until you've unlinked all external services.

    After importing the backup of your production system, simply run::
    
        source ~/.virtualenvs/dsmrreader/bin/activate
        ./manage.py development_reset

    This will remove all API keys and other links to externals systems, as well as reset the admin user credentials to ``admin / admin`` (user / password). 


Fake datalogger
---------------

There is a builtin command that can somewhat fake a datalogger::
    
    source ~/.virtualenvs/dsmrreader/bin/activate
    ./manage.py dsmr_fake_datasource --with-gas --with-electricity-returned

It will generate random data every second in a certain pattern and should be fine for basic testing. 

Please note that it only inserts unprocessed readings, so you'll still have to run the ``./manage.py dsmr_backend --run-once`` command to have the readings processed.


Running DSMR-reader locally
---------------------------

You can run the Django development server with::

    source ~/.virtualenvs/dsmrreader/bin/activate
    ./manage.py runserver

The application will be accessible on: ``http://localhost:8000/``.
Any code changes you make will let the application reload automatically.


Tests and coverage
------------------

DSMR-reader's test coverage should remain as high as possible. Running tests will also analyze the test coverage in detail. 

The easiest way to run tests is to use the in-memory tests::

    source ~/.virtualenvs/dsmrreader/bin/activate
    ./tools/quick-test.sh
    
To test a single app within DSMR-reader, just append it::

    source ~/.virtualenvs/dsmrreader/bin/activate
    ./tools/quick-test.sh dsmr_frontend

To test all database backends, run::

    source ~/.virtualenvs/dsmrreader/bin/activate
    ./tools/test-all.sh

The test coverage should be visible in the terminal after running tests.
There are detailed HTML pages available as well, after each test run, in ``coverage_report/html/index.html``. 
Just open it with your browser to view the test coverage of each file and line.

.. note::

    A side effect of running tests is that it may also regenerate .PO files from the ``docs/`` folder. 
    If you did not make any changes there, your should just ignore those changed files and revert them.
    

Translations
------------

You can find the translations (.PO files) for the main application in ``dsmrreader/locales/``.
To regenerate them, just execute the ``./tools/quick-test.sh`` script, as one of the tests checks translations.


Editing documentation
---------------------

The documentation is part of the repository and can be generated (automatically) with Sphinx::

    source ~/.virtualenvs/dsmrreader/bin/activate
    cd docs/
    sphinx-autobuild . _build/html -p 10000
    
You can now view the documentation in your browser by accessing: ``http://127.0.0.1:10000``.
Any changes you make will be reflected instantly in the browser, as Sphinx continuously checks for changed files.


Translating documentation
-------------------------

Translations are done using gettext and .PO files. Regenerate the .PO files with::

    source ~/.virtualenvs/dsmrreader/bin/activate
    cd docs/
    make gettext && sphinx-intl update -p _build/locale -l nl

The .PO files in ``docs/locale`` should be regenerated now. You can use ``poedit`` to view and translate the files.

After editing the .PO files, you can check the result by building the Dutch translations locally::

    make -e SPHINXOPTS="-D language='nl'" html

Now view the generated HTML in your browser by opening: ``docs/_build/html/index.html``


Pull requests
-------------

Please make sure to always point any pull requests to the ``development`` branch of DSMR-reader, as the ``master`` branch will only be affected by release merges.
