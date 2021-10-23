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

Execute the following::

    sudo su - dsmr
    ./deploy.sh

