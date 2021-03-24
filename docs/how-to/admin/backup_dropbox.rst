Admin: Backup & Dropbox
=======================

The application backs up your data daily. You can change the time the backup will be created every day.

.. image:: ../../_static/screenshots/v4/admin/backupsettings.png
    :target: ../../_static/screenshots/v4/admin/backupsettings.png
    :alt: Backup

You can use your Dropbox-account to make sure your backups are safely stored in your account.

.. image:: ../../_static/screenshots/v4/admin/dropboxsettings.png
    :target: ../../_static/screenshots/v4/admin/dropboxsettings.png
    :alt: Dropbox

Make sure you have a Dropbox-account or sign up for one. 
Now go to `Dropbox Apps <https://www.dropbox.com/developers/apps>`_ and click **"Create app"** in top right corner.

.. image:: ../../_static/faq/dropbox_apps_overview.png
    :target: ../../_static/faq/dropbox_apps_overview.png
    :alt: Dropbox Apps

Choose the option: (1) **Scoped access** and (2) **App folder**. 
Then enter a name for your app (3), this will also be used as the directory name within the Apps-folder of your Dropbox. 

Set the permissions on the **Permissions** tab. Check the boxes for **files.metadata.write**, **files.metadata.read**, **files.content.write** and **files.content.read**. Then click **Submit**.

On the **Settings** tab set **Access token expiration** to **No expiration** and click the **Generate** button below **Generated access token**.

Copy the generated access token to the DSMR-reader settings for the Dropbox-configuration. The DSMR-reader application should sync any backups created shortly.

Check the `backend logs <https://dsmr-reader.readthedocs.io/en/latest/how-to/troubleshooting/logfiles.html>`_ if the backup files do not appear in the dropbox folder.
