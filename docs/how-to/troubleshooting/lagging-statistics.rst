Common error resolution: How do I fix ``Day statistics are lagging behind``?
============================================================================

The error::

    Day statistics are lagging behind (1 day, 16 hours ago)

Means that the statistics module did not run (successfully) or lacks new data. This module runs once a day, by default at midnight.

Due to unforeseen circumstances the module may have not ran. E.g. caused by power outage or restart of the docker image.

Wait until the next scheduled run and see if the problem gets resolved automatically.
Alternatively (if you can't wait), go to ``/admin/dsmr_backend/scheduledprocess/`` and change the scheduled time of the ``Generate day and hour statistics`` task into the past, causing it to be executed momentarily.

If that doesn't resolve the issue, dive into the DEBUG logs and try to find the problem.

.. hint::

    Check the logs for ``Stats:`` statements, which may identify a root cause.

.. seealso::

    :doc:`See here for how to enable DEBUG logging </how-to/troubleshooting/enabling-debug-logging>`.
