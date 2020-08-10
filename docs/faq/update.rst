FAQ: Updating the application
=============================

Every once in a while there may be updates. You can also easily check for updates by using the application's Status page.

.. warning::
    
    First, **please make sure you have a recent backup of your database**! :doc:`More information about backups can be found here<../data_integrity>`.

You can update your application to the latest version by executing ``deploy.sh``, located in the root of the project.
Make sure to execute it while logged in as the ``dsmr`` user::

   sudo su - dsmr
   ./deploy.sh
