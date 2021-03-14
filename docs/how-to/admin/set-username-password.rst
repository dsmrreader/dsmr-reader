Admin: Setting or changing username/password
============================================

.. hint::

    There is no default user or password.
    You will need to set it yourself with the steps below, depending on whether you've installed manually or using Docker.


Manual installation
^^^^^^^^^^^^^^^^^^^

- Now execute::

    sudo su - dsmr
    ./manage.py createsuperuser --email dsmr@localhost --username admin

    # You will be asked to choose and enter a password twice. The email address is not used.

- Did it error with ``Error: That username is already taken.``? Then try::

    ./manage.py changepassword admin

- The user should be created (or its password should be reset).


Docker installation
^^^^^^^^^^^^^^^^^^^

The ``DSMRREADER_ADMIN_USER`` and ``DSMRREADER_ADMIN_PASSWORD`` :doc:`as defined in Env Settings</reference/env-settings>` will be used for the credentials.

Creating or updating credentials:

- Configure ``DSMRREADER_ADMIN_USER`` and ``DSMRREADER_ADMIN_PASSWORD`` of the :doc:`Env Settings</reference/env-settings>`.

- Now execute::

    sudo su - dsmr
    ./manage.py dsmr_superuser

- The user should be created (or its password should be reset).
