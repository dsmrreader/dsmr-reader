Upgrading to DSMR-reader v4.x
=============================

DSMR-reader ``v4.x`` is backwards incompatible with ``3.x``. You will have to manually upgrade to make sure it will run properly.

.. note::

    If you're using Docker, you can probably just install the ``v4.x`` version of the Docker container without any of the steps below.


1. Update to the latest ``v3.x`` version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:doc:`See here for instructions<update>`.


2. Python version
^^^^^^^^^^^^^^^^^

The minimum Python version required is unchanged in this release. It's still ``Python 3.6`` or higher.


3. Install python3-psycopg2
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're using PostgreSQL, the default for DSMR-reader, install the following system package::

    sudo apt-get install python3-psycopg2

Execute the following::

    sudo supervisorctl stop all

    sudo su - dsmr
    deactivate
    cd ~
    mv .virtualenvs/dsmrreader .virtualenvs/v3-dsmrreader

    virtualenv /home/dsmr/.virtualenvs/dsmrreader --system-site-packages --python python3
    source ~/.virtualenvs/dsmrreader/bin/activate
    logout

.. note::

    If you're getting any errors, you can revert to the old version by running::

        sudo su - dsmr

        # One of these checkouts might fail, but it's okay:
        git checkout -b v3 origin/v3
        git checkout v3

        # Just make sure you're at v3 now:
        git branch

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

Everything okay? Time to upgrade DSMR-reader to v4.x.


4. Switching DSMR-reader to ``v4.x``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

    # Now redeploy
    ./deploy.sh

    # (Re)start all processes
    logout
    sudo supervisorctl restart all

Great. You should now be on ``v4.x``!