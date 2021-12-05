Common error resolution: How do I fix ``Day statistics are lagging behind (1 day, 16 hours ago)``?
=============================================================================

The error::

    `Day statistics are lagging behind (1 day, 16 hours ago)` or similar

Means that the statistics module did not run or did not run succesfully. This module runs once a day, by default at midnight. Due to unforeseen the module may have not ran, for instance power outage or restart of the docker image.

Wait until the next scheduled run and see if the problem gets resolved automatically. Alternatively (if you can't wait), change the scheduled time by going to 
http://<your-ip>:<port>/admin/dsmr_backend/scheduledprocess/
and change the time of 
```Generate day and hour statistics```
and wait a bit.

If that doesn't resolve the issue, dive into the DEBUG logs and try to find the problem.
