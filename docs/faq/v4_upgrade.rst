Upgrading to DSMR-reader v4.x
=============================

DSMR-reader ``v4.x`` is backwards incompatible with ``3.x``. You will have to manually upgrade to make sure it will run properly.


1. Update to the latest ``v3.x`` version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:doc:`See here for instructions<update>`.


2. Python version
^^^^^^^^^^^^^^^^^

The minimum Python version required is unchanged in this release. It's still ``Python 3.6`` or higher.


3. Switching DSMR-reader to ``v4.x``
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
    pip3 install -r dsmrreader/provisioning/requirements/postgresql.txt

    # Now redeploy
    ./deploy.sh

    # (Re)start all processes
    logout
    sudo supervisorctl restart all

Great. You should now be on ``v4.x``!