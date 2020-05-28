Data integrity
==============

.. warning::

    Read this section carefully if you are using any volatile storage, such as an SD card.


Storage
--------
This project was designed to run on a RaspberryPi, but it affects the lifetime of the storage severely.
The introduction of DSMR v5 smart meters strains the storage even more, due to the high amount of telegrams sent each second.

The default storage on RaspberryPis suffers greatly from this and can not be trusted to keep your data safe.
Eventually the storage will get corrupted and either make your data inaccessible, or it pretends to write data, while not storing anything at all.


Backups
-------
DSMR-reader does support automated backups, but since they are still stored on the same volatile storage, they can be corrupted as well.


Prevention
----------
The only thing you can do, is make sure to have your backups stored somewhere else, once in a while.
Using Dropbox to sync your backups does not protect them of all harm!
For now, it's recommended to use the mechanism for sending a small backup to a GMail account.

.. note::

    If you are more technical savy, you could opt to either install the database or the entire application on a server with storage that tends to wear less.
    You can use the RaspberryPi are a remote datalogger, preventing a lot of issues.

    :doc:`More information about using a remote datalogger here<installation/datalogger>`.


Pitfalls
--------
- SD cards' lifespan in this project vary from several weeks to some years, depending on the quality of the storage and the interval of telegrams sent by you smart meter.
- Backups are created daily, but rotated weekly! So it's possible that, at some point, the backups get corrupted as well since they're overwritten each week. And eventually they will get synchronized to Dropbox as well.

