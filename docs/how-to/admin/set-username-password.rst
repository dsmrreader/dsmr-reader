Admin: Setting or changing username/password
============================================

.. hint::

    There is no default user or password.
    You will need to set it yourself with the steps below, depending on whether you've installed manually or using Docker.

Manual installation
^^^^^^^^^^^^^^^^^^^

- Set superuser credentials by opening the ``.env`` file with your favourite text editor::

    sudo su - dsmr

    # Or use "nano" or whatever
    vi .env

- Find (or add) these lines::

    # In /home/dsmr/dsmr-reader/.env

    DSMRREADER_ADMIN_USER=
    DSMRREADER_ADMIN_PASSWORD=

.. tip::
    Set the admin username and password you'd like. E.g.::

        DSMRREADER_ADMIN_USER=admin
        DSMRREADER_ADMIN_PASSWORD=supersecretpassword

Now have DSMR-reader create/reset the admin user for you.

- Execute::

    ./manage.py dsmr_superuser

- The user should be created (or its password should be reset).


Docker installation
^^^^^^^^^^^^^^^^^^^

The ``DSMRREADER_ADMIN_USER`` and ``DSMRREADER_ADMIN_PASSWORD``, :doc:`as defined in Env Settings</reference/env-settings>`, will be used for the credentials.

Creating or updating credentials:

- Configure ``DSMRREADER_ADMIN_USER`` and ``DSMRREADER_ADMIN_PASSWORD`` of the :doc:`Env Settings</reference/env-settings>`.

- Now execute::

    sudo su - dsmr
    ./manage.py dsmr_superuser

- The user should be created (or its password should be reset).
