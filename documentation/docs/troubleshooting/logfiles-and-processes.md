---
hide:
  - toc
---

# Logs and debugging

DSMR-reader technically consists of these processes:

| Process      | Name                | Description                                                                                                                                     |
|--------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Backend      | `dsmr_backend`      | Handles all background processing, such as telegram processing, MQTT, backups, health checks and everything that runs without user-interaction. |
| Datalogger   | `dsmr_datalogger`   | Local datalogger reading telegrams (if used).                                                                                                   |
| Webinterface | `dsmr_webinterface` | Graphical interface of DSMR-reader.                                                                                                             |


``` mermaid
graph LR
  A{Which logs?};
  A --->|Database issues| B[View DSMRDB logs];
  A --->|DSMR-reader issues| C[View DSMR logs];
  C -->D{Found cause?}
  D -->|No| E([Enable DEBUG logging])
  E ---->|Try one more last time| C
```

### DSMRDB logs

- Login as the `dsmrreader` user and run:

```shell
podman-compose logs -f dsmrdb

# Or when there are a lot of old logs, you can limit it to recent logs only:
podman-compose logs --since 30s -f dsmrdb
```

### DSMR logs
You can view logs of all processes combined.

- Login as the `dsmrreader` user and run:

```shell
sudo su - dsmrreader

podman-compose logs -f dsmr
# Or when there are a lot of old logs, you can limit it to recent logs only:
podman-compose logs --since 30s -f dsmr
```

### DEBUG logging
By default, mostly errors are logged. You can enable DEBUG logging which will make **specifically** the backend log greatly more verbose.

!!! tip "Heads up"

    Errors are likely to be logged at all times, no matter the logging level used.
    DEBUG logging is only helpful to watch DSMR-reader's detailed behaviour, when debugging issues.
    
    The DEBUG logging is **disabled by default**, to reduce the number writes on the filesystem.
    

You can enable the DEBUG logging by setting the `DSMRREADER_LOGLEVEL` env var to `DEBUG`. Follow these steps:

- Login as the `dsmrreader` user and edit the `compose.yml` file:

```shell
sudo su - dsmrreader
vi compose.yml
```

```yaml
# Simplified compose.yml - Find DSMRREADER_LOGLEVEL=DEBUG
services:
    dsmr:
        environment:
            # Remove the leading "###" to enable DEBUG logging. Or add "- DSMRREADER_LOGLEVEL=DEBUG" if you used a different Compose template.
            ###- DSMRREADER_LOGLEVEL=DEBUG
```

!!! warning "Caution"

    Don't forget to **disable** DEBUG logging again whenever you are done debugging.

- Apply changes:

```shell
podman-compose restart dsmr
```
