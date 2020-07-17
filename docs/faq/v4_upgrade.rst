Upgrading to DSMR-reader v4.x
=============================

DSMR-reader ``v4.x`` is backwards incompatible with ``3.x``. You will have to manually upgrade to make sure it will run properly.

.. note::

    If you're using Docker, you can probably just install the ``v4.x`` version of the Docker container without having to perform any of the steps below.


.. contents::
    :depth: 2

List of changes
^^^^^^^^^^^^^^^

:doc:`See the changelog<../changelog>`, for ``v4.x releases`` and higher. Check them before updating!


1. Update to the latest ``v3.x`` version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:doc:`See here for instructions<update>`.


2. Install ``python3-psycopg2``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're using PostgreSQL, the default for DSMR-reader, install the following system package::

    sudo apt-get install python3-psycopg2

Execute the following::

    sudo supervisorctl stop all

    sudo su - dsmr
    deactivate
    cd ~
    mv .virtualenvs/dsmrreader .virtualenvs/v3-dsmrreader

    virtualenv /home/dsmr/.virtualenvs/dsmrreader --system-site-packages --python python3

    # Check Python version. Should be v3.6.x or higher:
    source ~/.virtualenvs/dsmrreader/bin/activate
    python3 --version

    logout

.. warning::

    If you've installed Python ``3.6`` or higher manually and the default Python version is below ``3.6``, make sure to specify it in the ``virtualenv`` command above.

    For example::

        virtualenv /home/dsmr/.virtualenvs/dsmrreader --system-site-packages --python python3.6

.. note::

    If you're getting any errors, you can revert to the old version by running::

        sudo su - dsmr

        deactivate
        cd ~
        mv .virtualenvs/dsmrreader .virtualenvs/v4-dsmrreader
        mv .virtualenvs/v3-dsmrreader .virtualenvs/dsmrreader

        # Now redeploy
        logout
        sudo su - dsmr
        ./deploy.sh

        # (Re)start all processes
        logout
        sudo supervisorctl restart all


3. Switch DSMR-reader to ``v4.x``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DSMR-reader ``v4.x`` lives in a different branch, to prevent any users from unexpectedly updating to ``v4.x``.

Execute the following::

    sudo supervisorctl stop all

    sudo su - dsmr
    git fetch
    git checkout -b v4 origin/v4

    # Make sure you're at v4 now:
    git branch

    git pull
    pip3 install -r dsmrreader/provisioning/requirements/base.txt

    logout


4. Migrate ``settings.py`` to ``.env``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DSMR-reader started with a ``settings.py`` for your local settings.
This has some disadvantages, especially regarding today's industry standards and how Docker works as well.

Therefor the configuration has been migrated to a ``.env`` file and system env vars are now supported as well. Follow these steps to migrate::

    sudo su - dsmr
    mv dsmrreader/settings.py dsmrreader/settings.py.BACKUP
    cp dsmrreader/provisioning/django/settings.py.template dsmrreader/settings.py

    cp .env.template .env

Now check the settings you were using in ``dsmrreader/settings.py.BACKUP``.
Compare them with the defaults in ``.env``.

If you find any differences (e.g. different database credentials or host), update the ``.env`` file accordingly. The format should be straight forward.

Not all previously supported settings are also available in ``.env``.
See :doc:`Env Settings for the latest list of env vars supported<../env_settings>`.

Backwards incompatible
----------------------

Please note that ``DSMRREADER_PLUGINS`` is now a comma separated list.
Chances are however very slim that you were using ``DSMRREADER_PLUGINS`` at all (advanced users only).

Execute the following::

    logout


5. Generate your own ``SECRET_KEY``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Previous versions had a hardcoded value for ``SECRET_KEY``.
This was fine while running DSMR-reader in your home network, but it is not recommended for public facing instances.

To prevent some users from forgetting to set a custom secret key, DSMR-reader now simply requires everyone to generate a unique ``SECRET_KEY`` locally during installation (or when upgrading).

Execute the following::

    sudo su - dsmr
    ./tools/generate-secret-key.sh

Check whether the script updated your ``.env`` file properly::

    grep 'SECRET_KEY=' .env

It should display the key generated when you execute it.

Check the configuration with::

    ./manage.py check
    logout

.. note::

    If you run into the following error::

        Error loading psycopg2 module: No module named 'psycopg2._psycopg'

    Revert the ``psycopg2`` installation above with::

        logout
        sudo apt-get remove python3-psycopg2

        sudo su - dsmr
        pip3 install psycopg2-binary --upgrade

        # Try again:
        ./manage.py check


Execute the following::

    logout

6. Drop ``dsmr_mqtt``
^^^^^^^^^^^^^^^^^^^^^

The ``dsmr_mqtt`` process has been merged with to ``dsmr_backend``.


Execute the following::

    sudo supervisorctl status

Is ``dsmr_mqtt`` listed? If **not listed**, skip this chapter. Otherwise remove it::

    sudo rm /etc/supervisor/conf.d/dsmr_mqtt.conf

* Apply changes::

    sudo supervisorctl reread
    sudo supervisorctl update

    sudo supervisorctl restart all

Execute the following::

    sudo supervisorctl status

You should not see ``dsmr_mqtt`` anymore.

Also, the other processes should be running as well again.

7. Deploy
^^^^^^^^^
Finally, execute the deploy script::

    sudo su - dsmr
    ./deploy.sh

Great. You should now be on ``v4.x``!
