Frequently Asked Questions (FAQ)
================================


.. contents::
    :depth: 2


I need help!
------------
If you can't find the answer in the documentation, do not hesitate in looking for help.

.. seealso::

    `Create an issue at Github <https://github.com/dsmrreader/dsmr-reader/issues/new>`_.


How can I update my application?
--------------------------------

.. seealso::

    :doc:`More information can be found here <faq/update>`.


How can I downgrade my application?
-----------------------------------

.. seealso::

    :doc:`More information can be found here <faq/downgrade>`.


How can I move the database location?
-------------------------------------

.. seealso::

    :doc:`More information can be found here <faq/database>`.


Recalculate prices retroactively
--------------------------------
*I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?*

Execute::

    sudo su - dsmr
    ./manage.py dsmr_stats_recalculate_prices


I'm not seeing any gas readings
-------------------------------

Please make sure that your meter supports reading gas consumption and that you've waited for a few hours for any graphs to render. 
The gas meter positions are only be updated once per hour (for DSMR v4).
The Status page will give you insight in this as well.


How do I restore a database backup?
-----------------------------------

.. seealso::

    :doc:`More information can be found here <installation/restore>`.


How do I enable timezone support for MySQL?
-------------------------------------------

.. seealso::

    `Check these docs <https://dev.mysql.com/doc/refman/5.7/en/mysql-tzinfo-to-sql.html>`_ for more information about how to enable timezone support on MySQL.

On recent versions it should be as simple as executing the following command as root/sudo user::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql


How do I retain MQTT support when upgrading to v1.23.0 or higher?
-----------------------------------------------------------------

.. seealso::

    :doc:`More information can be found here <mqtt>`.


How do I uninstall DSMR-reader?
-------------------------------

.. seealso::

    :doc:`More information can be found here <faq/uninstall>`.


How can I use the datalogger only and forward the telegrams?
------------------------------------------------------------

.. seealso::

    :doc:`More information can be found here <installation/datalogger>`.


How can I check the logfiles?
-----------------------------

.. seealso::

    :doc:`More information can be found here <troubleshooting>`.


How can I restart the application or processes?
-----------------------------------------------

.. seealso::

    :doc:`More information can be found here <faq/restart_processes>`.


How do I fix errors such as ``DETAIL: Key (id)=(123) already exists``?
----------------------------------------------------------------------

This depends on the situation, but you can always try this yourself first::

    # Note: dsmr_sqlsequencereset is only available in DSMR-reader v3.3.0 and higher
    sudo su - dsmr
    ./manage.py dsmr_sqlsequencereset

If it does not resolve your issue, `ask for support <#i-need-help>`_.


I've changed to a different smart meter
---------------------------------------
Sometimes, when relocating or due to replacement of your meter, the meter positions read by DSMR-reader will cause invalid data (e.g.: big gaps or inverted consumption).
Any consecutive days should not be affected by this issue, so you will only have to adjust the data for one day.

The day after, you should be able to manually adjust any invalid Day or Hour Statistics :doc:`in the admin interface<configuration>` for the invalid day.


How can I create the (super)user or update its password?
--------------------------------------------------------

.. seealso::

    :doc:`Env Settings<env_settings>`.

Configure ``DSMR_USER`` and ``DSMR_PASSWORD`` of the :doc:`Env Settings<env_settings>`.

Now execute::

    sudo su - dsmr
    ./manage.py dsmr_superuser

The user should either be created or the existing user should have its password updated.


How do I fix: ``Error: Already running on PID 1234 (or pid file '/var/tmp/gunicorn--dsmr_webinterface.pid' is stale)``?
-----------------------------------------------------------------------------------------------------------------------
Just delete the PID file and restart the webinterface::

    sudo supervisorctl restart dsmr_webinterface
