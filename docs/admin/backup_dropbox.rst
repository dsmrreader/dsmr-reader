Admin: Backup & Dropbox
=======================

The application backs up your data daily. You can change the time the backup will be created every day.

.. image:: ../_static/screenshots/v4/admin/backupsettings.png
    :target: ../_static/screenshots/v4/admin/backupsettings.png
    :alt: Backup

You can use your Dropbox-account to make sure your backups are safely stored in your account.

.. image:: ../_static/screenshots/v4/admin/dropboxsettings.png
    :target: ../_static/screenshots/v4/admin/dropboxsettings.png
    :alt: Dropbox

Make sure you have a Dropbox-account or sign up for one. 
Now go to `Dropbox Apps <https://www.dropbox.com/developers/apps>`_ and click **"Create app"** in top right corner.

.. image:: ../_static/faq/dropbox_apps_overview.png
    :target: ../_static/faq/dropbox_apps_overview.png
    :alt: Dropbox Apps

Choose the following options: (1) **Dropbox API** and (2) **App folder**. 
Then enter a name for your app (3), this will also be used as directory name within the Apps-folder of your Dropbox. 

.. image:: ../_static/faq/dropbox_create_app.png
    :target: ../_static/faq/dropbox_create_app.png
    :alt: Dropbox Apps

The app should be created in developer-mode. You can generate an access token for yourself by clicking the **"Generate"** button somewhere below.
    
.. image:: ../_static/faq/dropbox_app_token.png
    :target: ../_static/faq/dropbox_app_token.png
    :alt: Dropbox Apps
    
Copy the generated access token to the DSMR-reader settings for the Dropbox-configuration. The DSMR-reader application should sync any backups created shortly.
