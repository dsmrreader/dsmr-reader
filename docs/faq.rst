Frequently Asked Questions (FAQ)
================================


.. contents::
    :depth: 2


I need help!
------------
If you can't find the answer in the documentation, do not hesitate in looking for help.

`Create an issue at Github <https://github.com/dennissiemensma/dsmr-reader/issues/new>`_


How can I update my application?
--------------------------------

:doc:`See for instructions here <faq/update>`.


How can I move the database location?
-------------------------------------
:doc:`See for instructions here <faq/database>`.

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

:doc:`See for instructions here <installation/restore>`.


How do I enable timezone support for MySQL?
-------------------------------------------

`Check these docs <https://dev.mysql.com/doc/refman/5.7/en/mysql-tzinfo-to-sql.html>`_ for more information about how to enable timezone support on MySQL.
On recent versions it should be as simple as executing the following command as root/sudo user::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql


How do I retain MQTT support when upgrading to v1.23.0 or higher?
-----------------------------------------------------------------

:doc:`See for instructions here <mqtt>`.


How do I uninstall DSMR-reader?
-------------------------------

:doc:`See for instructions here <faq/uninstall>`.


How can I use the datalogger only and forward the telegrams?
------------------------------------------------------------

See :doc:`these datalogger instructions<installation/datalogger>` for more information.


How can I check the logfiles?
-----------------------------

:doc:`See for instructions here <troubleshooting>`.


How can I restart the application or processes?
-----------------------------------------------

:doc:`See for instructions here <faq/restart_processes>`.

How do I fix errors such as ``DETAIL: Key (id)=(123) already exists``?
----------------------------------------------------------------------

This depends on the situation, but you can always try this yourself first::

    # Note: dsmr_sqlsequencereset was added in DSMR-reader v3.3.0+
    sudo su - dsmr
    ./manage.py dsmr_sqlsequencereset

If it does not resolve your issue, `ask for support <#i-need-help>`_.
