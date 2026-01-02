# Errors

Common error messages and their solutions.

!!! abstract ""

    Note that we are using `podman-compose`, everywhere, and **not** `podman compose` (note the dash/whitespace difference). Using the latter will result in different behavior!

## Key (id) already exists

```sql
Key (id)=(1292) already exists.
```

This depends on the situation, but you can always try the following yourself first:

```shell
sudo su - dsmrreader
podman-compose exec dsmr /app/manage.py dsmr_sqlsequencereset
```

!!! tip
    
    **See also:** If it does not resolve your issue, ask for support on GitHub.

----

## Day statistics are lagging behind

```
Day statistics are lagging behind (1 day, 16 hours ago)
```

This means that the statistics process did not run (successfully) or lacks new data. This module runs once a day, by default at midnight.

Due to unforeseen circumstances the process may have not run. But it can also just wait for new data to arrive. E.g. caused by power outage or server restart.

Wait until the next scheduled run and see if the problem gets resolved automatically. 
Alternatively:

- Go to `/admin/dsmr_backend/scheduledprocess/`.
- Change the scheduled time of the `Generate day and hour statistics` task into the **past** (or "now"). It should run shortly.
- If that doesn't resolve the issue, try [Logs and debugging](logs-debugging.md).

!!! tip
    
    Check the logs for `Stats:` statements, which may identify a root cause.

----

## Warning "Too many outgoing MQTT messages queued for transit"

If this happens, either DSMR-reader is creating MQTT-messages faster than your MQTT broker can handle, or your MQTT broker is not reachable.

Whatever the reason, if you want to clear the queue **which will permanently delete all those pending messages**, you can do so by running:

```shell
sudo su - dsmrreader
podman-compose exec dsmr /app/manage.py dsmr_mqtt_clear_queue
```

----

## Warning "Too many outgoing InfluxDB measurements queued for transit"

Similar to MQTT above, this will clear the InfluxDB queue **permanently deleting all those pending measurements**:

```shell
sudo su - dsmrreader
podman-compose exec dsmr /app/manage.py dsmr_influxdb_clear_queue
```
