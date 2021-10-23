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

Update to ``v4.20.0`` to ensure you have the latest ``v4.x`` version.



2. Relocate to https://github.com/dsmrreader
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Over a year ago the DSMR-reader project was moved to `https://github.com/dsmrreader`.


Execute the following::

    sudo su - dsmr
    git remote -v


It should point to::


    origin	https://github.com/dsmrreader/dsmr-reader.git (fetch)
    origin	https://github.com/dsmrreader/dsmr-reader.git (push)


If not, update it and check again::

    git remote set-url origin https://github.com/dsmrreader/dsmr-reader.git
    git remote -v

