Guide: Upgrading DSMR-reader v4.x to v5.x
=========================================

DSMR-reader ``v5.x`` is backwards incompatible with ``4.x``. You will have to manually upgrade to make sure it will run properly.

.. note::

    If you're using Docker, you can probably just install the ``v5.x`` version of the Docker container without having to perform any of the steps below.


.. contents::
    :depth: 2

List of changes
^^^^^^^^^^^^^^^

:doc:`See the changelog</reference/changelog>`, for ``v5.x releases`` and higher. Check them before updating!


1. Update to the latest ``v4.x`` version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update to ``v4.20`` to ensure you have the latest ``v4.x`` version.


2. Relocate to github.com/dsmrreader/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Over a year ago the DSMR-reader project was moved to ``https://github.com/dsmrreader``.


Execute the following::

    sudo su - dsmr
    git remote -v


It should point to::


    origin	https://github.com/dsmrreader/dsmr-reader.git (fetch)
    origin	https://github.com/dsmrreader/dsmr-reader.git (push)


**If not**, update it and check again::

    git remote set-url origin https://github.com/dsmrreader/dsmr-reader.git
    git remote -v

Execute the following::

    logout


3. Python version check
^^^^^^^^^^^^^^^^^^^^^^^

DSMR-reader ``5.x`` requires ``Python 3.7`` or higher.

Execute the following::

    sudo su - dsmr
    python3 --version

It should display the Python version. **If you're already running** ``Python 3.7`` **(or higher), you can ignore the next section.**

Execute the following::

    logout

4. Python version upgrade (when running ``Python 3.6`` or lower)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

    Only execute this section if you're running DSMR-reader with ``Python 3.6`` or lower!

There are several guides, depending on your OS. We assume Raspbian OS here.

.. tip::

    You may consider upgrading to a higher Python version, e.g. ``Python 3.9``, if possible for your OS.


Execute the following::

    # Credits to Jeroen Peters @ issue #624
    sudo apt-get install python3-dev libffi-dev libssl-dev -y
    wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tar.xz
    tar xJf Python-3.9.9.tar.xz
    cd Python-3.9.9
    ./configure
    make
    sudo make install
    sudo pip3 install --upgrade pip

.. attention::

    Try running the command ``python3.9 --version`` to see if things worked out. If you're getting any errors, do not continue with the upgrade.

----

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

Execute the following::

    logout


5. Upgrade to DSMR-reader v5
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Remove the following line from ``/home/dsmr/.bashrc``::

    source ~/.virtualenvs/dsmrreader/bin/activate

Install Poetry::

    pip3 install --user --upgrade pip poetry

Add the following line to ``/home/dsmr/.bashrc``::

    poetry shell

Stop DSMR-reader::

    sudo supervisorctl stop all

Disable ``v4.x`` virtualenv::

    sudo su - dsmr
    deactivate
    mv ~/.virtualenvs/ ~/.old-v4-virtualenvs

Update DSMR-reader codebase::

    git fetch
    git checkout -b v5 origin/v5

    # Make sure you're at v5 now:
    git branch

    git pull

Install dependencies::

    poetry config virtualenvs.in-project true
    poetry install

Update Supervisor configs::

    logout

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/

Reload Supervisor configs::

   sudo supervisorctl reread

Start DSMR-reader::

    sudo supervisorctl start all


6. Deploy
^^^^^^^^^
Finally, execute the deploy script::

    sudo su - dsmr
    ./deploy.sh

Great. You should now be on ``v5.x``!
