Frequently Asked Questions (FAQ)
================================

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

Make sure you have a Mindergas.nl-account or `signup for one <https://www.mindergas.nl/users/sign_up>`_. 
Now go to "`Meterstand API <https://www.mindergas.nl/member/api>`_" and click on the button located below **"Authenticatietoken"**.
  
.. image:: _static/faq/mindergas_api.png
    :target: _static/faq/mindergas_api.png
    :alt: Mindergas API

Copy the authentication token generated and paste in into the DSMR-reader settings for the Mindergas.nl-configuration.
Obviously the export only works when there are any gas readings at all and you have ticked the 'export' checkbox in the Mindergas.nl-configuration as well.

Please note that due to policies of mindergas.nl it's not allowed to retroactively upload meter positions using the API. 
Therefor this is not supported by the application. You can however, enter them manually on their website. 


Recalculate prices
------------------
*I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?*

You can flush your statistics by executing:

``./manage.py dsmr_stats_clear_statistics --ack-to-delete-my-data``

The application will delete all statistics and (slowly) regenerate them in the background. Just make sure the source data is still there.


Feature/bug report
------------------
*How can I propose a feature or report a bug I've found?*

`Just create a ticket at Github <https://github.com/dennissiemensma/dsmr-reader/issues/new>`_
