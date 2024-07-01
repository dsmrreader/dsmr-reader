Updating DSMR-reader
====================

Every once in a while there may be updates. You can also easily check for updates by using the About page in DSMR-reader.

.. caution::

    First, **please make sure you have a recent backup of your database**!

You can update your application to the latest version by executing ``deploy.sh``, located in the root of the project.
Make sure to execute it while logged in as the ``dsmr`` user::

   sudo su - dsmr
   ./deploy.sh

This will update you to the latest minor version of the branch you're using.
It should always be backwards compatible and therefor safe to use at all times.

.. hint::

    For example, if you are running ``v4.x`` this will update you to the latest ``v4.y`` version. But not automatically to ``v5.x``.