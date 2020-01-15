Upgrading to DSMR-reader v3.x
=============================

DSMR-reader ``v3.x`` is backwards incompatible with ``2.x``. You will have to manually upgrade to make sure it will run properly.


1. Update to the latest ``v2.x`` version (``v2.15``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:doc:`See here for instructions<update>`.


2. Python version check
^^^^^^^^^^^^^^^^^^^^^^^

DSMR-reader ``3.x`` requires ``Python 3.6`` or higher.

Execute the following::

    sudo su - dsmr
    python3 --version

It should display the Python version. If you're already running ``Python 3.6`` (or higher), you can ignore the next section.


3. Python version upgrade (part 1/2)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

    Only execute this section if you're running DSMR-reader with ``Python 3.5`` or lower!

There are several guides, depending on your OS. We assume Raspbian OS here.

Execute the following::

    # Credits to Jeroen Peters @ issue #624
    sudo apt-get install python3-dev libffi-dev libssl-dev -y
    wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tar.xz
    tar xJf Python-3.6.9.tar.xz
    cd Python-3.6.9
    ./configure
    make
    sudo make install
    sudo pip3 install --upgrade pip

Try running the command ``python3.6 --version`` to see if things worked out. If you're getting any errors, do not continue with the upgrade.

The Python upgrade continues later, after creating a backup.

4. Backup
^^^^^^^^^
The next thing you'll absolutely need to do, is create a fresh database backup and store it somewhere safe.

Execute the following::

    sudo su - dsmr
    ./manage.py dsmr_backup_create --full

If things went well, you should see a message like::

    Created full backup: /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz

Execute the following (your file name may differ!)::

    ls -lh /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz

Make sure the file is of some (reasonable) size::

    -rw-rw-r-- 1 dsmr dsmr 7.5M Dec 18 20:59 /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz

Execute the following (your file name may differ!)::

    zcat /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz | tail

Make sure the output ends with::

    --
    -- PostgreSQL database dump complete
    --

5. Python version upgrade (part 2/2)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

    Only execute this section if you're running DSMR-reader with ``Python 3.5`` or lower!

Now we're ready to remove the environment DSMR-reader uses.

Execute the following::

    sudo su - dsmr
    deactivate
    cd ~
    mv .virtualenvs/dsmrreader .virtualenvs/v2-dsmrreader

    virtualenv /home/dsmr/.virtualenvs/dsmrreader --no-site-packages --python python3.6
    source ~/.virtualenvs/dsmrreader/bin/activate

.. note::

    If you're getting any errors, you can revert to the old version by running::

        sudo su - dsmr
        deactivate
        cd ~
        mv .virtualenvs/v2-dsmrreader .virtualenvs/dsmrreader

        cd dsmr-reader
        ./deploy.sh

Everything okay? Time to upgrade DSMR-reader to v3.x.

6. Switching DSMR-reader to ``v3.x``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DSMR-reader ``v3.x`` lives in a different branch, to prevent any users from unexpectedly updating to ``v3.x``.

Execute the following::

    sudo su - dsmr
    git fetch
    git checkout -b v3 origin/v3
    git pull
    pip3 install -r dsmrreader/provisioning/requirements/base.txt
    pip3 install -r dsmrreader/provisioning/requirements/postgresql.txt
    ./deploy.sh

Great. You should now be on ``v3.x``!