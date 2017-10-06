Frequently Asked Questions (FAQ)
================================


.. contents::
    :depth: 2


How can I update my application?
--------------------------------
The version you are running is always based on the 'latest' version of the application, called the `master` branch.
Every once in a while there may be updates. Since ``v1.5`` you can also easily check for updates by using the application's Status page.

.. warning::
    
    Before updating, **please make sure you have a recent backup of your database**! :doc:`More information about backups can be found here<application>`.

You can update your application to the latest version by executing **deploy.sh**, located in the root of the project. 
Make sure to execute it while logged in as the ``dsmr`` user::

   sudo su - dsmr
   ./deploy.sh

It will make sure to check, fetch and apply any changes released. Summary of deployment script steps:

- GIT pull (codebase update).
- PIP update requirements.
- Apply any database migrations.
- Sync static files to Nginx folder.
- Reload Gunicorn application server (web interface) and backend processes (such as the datalogger).
- Clear any caches.


Dropbox: Automated backup sync
------------------------------
*How can I link my Dropbox account for backups?*

Make sure you have a Dropbox-account or sign up for one. 
Now go to `Dropbox Apps <https://www.dropbox.com/developers/apps>`_ and click **"Create app"** in top right corner.

.. image:: _static/faq/dropbox_apps_overview.png
    :target: _static/faq/dropbox_apps_overview.png
    :alt: Dropbox Apps

Choose the following options: (1) **Dropbox API** and (2) **App folder**. 
Then enter a name for your app (3), this will also be used as directory name within the Apps-folder of your Dropbox. 

.. image:: _static/faq/dropbox_create_app.png
    :target: _static/faq/dropbox_create_app.png
    :alt: Dropbox Apps

The app should be created in developer-mode. You can generate an access token for yourself by clicking the **"Generate"** button somewhere below.
    
.. image:: _static/faq/dropbox_app_token.png
    :target: _static/faq/dropbox_app_token.png
    :alt: Dropbox Apps
    
Copy the generated access token to the DSMR-reader settings for the Dropbox-configuration. The DSMR-reader application should sync any backups created shortly.


Mindergas.nl: Automated gas meter position export
-------------------------------------------------
*How can I link my mindergas.nl account?*

Make sure you have a Mindergas.nl account or `signup for one <https://www.mindergas.nl/users/sign_up>`_. 
Now go to "`Meterstand API <https://www.mindergas.nl/member/api>`_" and click on the button located below **"Authenticatietoken"**.
  
.. image:: _static/faq/mindergas_api.png
    :target: _static/faq/mindergas_api.png
    :alt: Mindergas API

Copy the authentication token generated and paste in into the DSMR-reader settings for the Mindergas.nl-configuration.
Obviously the export only works when there are any gas readings at all and you have ticked the 'export' checkbox in the Mindergas.nl-configuration as well.

.. note::

    Please note that due to policies of mindergas.nl it's not allowed to retroactively upload meter positions using the API. 
    Therefor this is not supported by the application. You can however, enter them manually on their website. 


PVOutput.org: Automated electricity consumption export
------------------------------------------------------
*How can I link my PVOutput.org account?*

Make sure you have a PVOutput.org account, or `signup for an account <https://pvoutput.org/>`_.
You will have to configure your account and PV system(s). For any support doing that, please `see this page <https://pvoutput.org/help.html#overview-getting-started>`_ for more information.

In order to link DSMR-reader to your account, please write down the "API Key" and "System ID" from your PVOutput account. You can find them near the bottom of the "Settings" page in PVOutput.


.. image:: _static/faq/external_pvoutput_settings.png
    :target: _static/faq/external_pvoutput_settings.png
    :alt: PVOutput account settings


Enter those values in DSMR-reader's admin pages, at "PVOutput: API configuration". Make sure to enter both:

    * API Key
    * System ID


.. image:: _static/faq/pvoutput_api.png
    :target: _static/faq/pvoutput_api.png
    :alt: API settings
    
    
Now navigate to another settings page in DSMR-reader: "PVOutput: "Add Status" configuration". 

    * Enable uploading the consumption.
    * Choose an interval between the uploads. You can configure this as well on the PVOutput's end, in Device Settings.
    * Optionally, choose an upload delay X (in minutes). If set, DSMR-reader will not use data of the past X minutes. 
    * Optionally, you can choose to enter a **processing delay in minutes** for PVOutput. Please note that PVOutput will only allow this when you have a **"Donation" account** on their website. If you do not have one, they will reject each API call you make, until you disable (clear) this option in DSMR-reader. 
    
    
.. image:: _static/faq/pvoutput_add_status.png
    :target: _static/faq/pvoutput_add_status.png
    :alt: Add Status settings

If you configured everything correctly, you should see some addional data in PVOutput listed under "Your Outputs" momentarily.


Usage notification: Daily usage statistics on your smartphone
-------------------------------------------------------------
*Which services for sending notifications are supported?*

Currently, two mobile platforms are supported: Android and iOS.
The supported app for Android is `NotifyMyAndroid <https://www.notifymyandroid.com>`_. 
The supported app for iOS is `Prowl <https://www.prowlapp.com>`_. 


*How do I setup usage notifications?*

Make sure you either have NotifyMyAndroid or Prowl installed on your smartphone. If you don't, visit your platforms app store to download the app and sign up for an account. Then, make sure to get your API key from the notificationservice that you prefer. For instruction on obtaining the API key, please read below.

In the DSMR-reader settings for the Usagenotifications, tick the Send Notifications checkbox and select the notification service you want to use. Then copy the API key from the notification service and paste in into the the textbox for the API key. When you save these settings, your first notification should be sent after midnight. Don't worry, the notification will be sent with low priority and will not wake you up.


*How do I obtain my API key for NotifyMyAndroid?*

After you have downloaded NotifyMyAndroid and signed up for an account you should be able to `login to your NotifyMyAndroid account <https://www.notifymyandroid.com/index.jsp>`_. 
Now go to "`My Account <https://www.notifymyandroid.com/account.jsp>`_", you should see an overview of your current API keys if you have any. To create an API key for the DSMR-reader, please click **"Generate New Key"**.

.. image:: _static/faq/notifications-notify-my-android-create-key.png
    :target: _static/faq/notifications-notify-my-android-create-key.png
    :alt: NotifyMyAndroid My Account overview
    
When a new key is generated, you will see it immediatly. Your key is listed like in the screenshot below (the red box marks your API key).

.. image:: _static/faq/notifications-notify-my-android-get-key.png
    :target: _static/faq/notifications-notify-my-android-get-key.png
    :alt: NotifyMyAndroid Get Your API Key


*How do I obtain my API key for Prowl?*

After you have downloaded Prowl and signed up for an account you should be able to `login to your Prowl account <https://www.prowlapp.com/login.php>`_. 
Now go to "`API Keys <https://www.prowlapp.com/api_settings.php>`_", you should see an overview of your current API keys if you have any. To create an API key for the DSMR-reader, input a name and click **"Generate Key"**.

.. image:: _static/faq/notifications-prowl-create-key.png
    :target: _static/faq/notifications-prowl-key.png
    :alt: Prowl My Account overview
    
When a new key is generated, you will see it immediatly. Your key is listed like in the screenshot below (the red box marks your API key).

.. image:: _static/faq/notifications-prowl-get-key.png
    :target: _static/faq/notifications-prowl-get-key.png
    :alt: Prowl Get Your API Key


I only pay for a single electricity tariff but I see two!
---------------------------------------------------------
DSMR (and your energy supplier) always read both high and low tariff from your meter. 
It's possible however that you are only paying for a single tariff. 
In that case your energy supplier will simply merge both high and low tariffs to make it look like you have a single one.

This application displays separate tariffs by default, but supports merging them to a single one as well.
Just make sure that you apply the **same price to both electricity 1 and 2** and enable the option ``Merge electricity tariffs`` in the frontend configuration.


I want to see the load of each electricity phase as well
---------------------------------------------------------
Since ``DSMR-reader v1.5`` it's possible to track your ``P+`` (consumption) phases as well. You will need to enable this in the ``Datalogger configuration``.
There is a setting called ``Track electricity phases``. When active, this will log the current usage of those phases and plot these on the Dashboard page.

Please keep in mind:

- This will **not work retroactively**. The datalogger always discards all data not used.
- This feature will only work when your smart meter is connected to **three phases**. Even when having the setting enabled.
- When having tracking phases enabled, you should see a button in the Dashboard called ``Display electricity phases``. Click on it to show the graph.

You should see something similar to:

.. image:: _static/screenshots/phases.png
    :target: _static/screenshots/phases.png
    :alt: Phases


Recalculate prices retroactively
--------------------------------
*I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?*

Statistics for each day are generated once, the day after. However, you can flush your statistics by executing:

``./manage.py dsmr_backend_delete_aggregated_data``

The application will delete all statistics and (slowly) regenerate them in the background. Just make sure the source data is still there.


I'm not seeing any gas readings
-------------------------------
Please make sure that your meter supports reading gas consumption and that you've waited for a few hours for any graphs to render. 
The gas meter positions are only be updated once per hour (for DSMR v4).
The Status page will give you insight in this as well.


How do I restore a database backup?
-----------------------------------

.. warning::

    Restoring a backup will replace any existing data stored in the database and is irreversible! 

.. note::

    Do you need a complete reinstall of DSMR-reader as well? 
    Then please :doc:`follow the install guide<installation>` and restore the database backup **using the notes at the end of chapter 1**. 

Only want to restore the database?

- This asumes you are still running the same application version as the backup was created in.

- Stop the application first with ``sudo supervisorctl stop all``. This will disconnect it from the database as well.

- Importing the data could take a long time. It took MySQL 15 minutes to import nearly 3 million readings, from a compressed backup, on a RaspberryPi 3. 

For **PostgreSQL** restores::

    sudo sudo -u postgres dropdb dsmrreader
    sudo sudo -u postgres createdb -O dsmrreader dsmrreader
    
    # Either restore an uncompressed (.sql) backup:
    sudo sudo -u postgres psql dsmrreader -f <PATH-TO-POSTGRESQL-BACKUP.sql>
    
    # OR
    
    # Restore a compressed (.gz) backup with:
    zcat <PATH-TO-POSTGRESQL-BACKUP.sql.gz> | sudo sudo -u postgres psql dsmrreader


For **MySQL** restores::

    sudo mysqladmin create dsmrreader
    sudo mysqladmin drop dsmrreader
    
    # Either restore an uncompressed (.sql) backup:
    cat <PATH-TO-MYSQL-BACKUP.sql.gz> | sudo mysql --defaults-file=/etc/mysql/debian.cnf -D dsmrreader
    
    # OR
    
    # Restore a compressed (.gz) backup with:
    zcat <PATH-TO-MYSQL-BACKUP.sql.gz> | sudo mysql --defaults-file=/etc/mysql/debian.cnf -D dsmrreader


- Start the application again with ``sudo supervisorctl start all``.

.. note::

    In case the version differs, you can try forcing a deployment reload by: ``sudo su - dsmr`` and then executing ``./post-deploy.sh``.


Feature/bug report
------------------
*How can I propose a feature or report a bug I've found?*

.. seealso::
    
    `Just create a ticket at Github <https://github.com/dennissiemensma/dsmr-reader/issues/new>`_.
