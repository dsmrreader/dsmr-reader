Database: Enabling timezone support (MySQL)
===========================================

.. caution::

    Even though DSMR-reader does not officially support MySQL/MariaDB, it should run fine.
    There is however one big gotcha: **You will need to enable timezone support.**

On recent versions it should be as simple as executing the following command as root/sudo user::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql

.. seealso::

    `Check these docs <https://dev.mysql.com/doc/refman/5.7/en/mysql-tzinfo-to-sql.html>`_ for more information about how to enable timezone support on MySQL.
