Admin: Email backup
===================

You can have the application email you a partial backup of the database daily, (bi)weekly or monthly.

.. warning::

    Please note that the backup being sent by email **only contains day/hour statistics** (as displayed in the Archive page).
    
    It should only be used in an emergency, when you are unable to restore a full backup of the database for some reason.


Before enabling this, make sure you've configured email settings as well, as the application needs an email server to do so.
:doc:`Go to email settings here.<email>`


.. image:: ../_static/screenshots/v4.7/admin/emailbackupsettings.png
    :target: ../_static/screenshots/v4.7/admin/emailbackupsettings.png
    :alt: Email backup settings
