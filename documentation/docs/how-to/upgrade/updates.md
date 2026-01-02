# Updates

DSMR-reader update process. To see (recent) updates check the [Changelog](../../reference/changelog.md){ .md-button }

## Major updates

!!! note ""
    
    When a new major version of DSMR-reader is released (e.g. ``v5.x`` to ``v6.0``) you need to follow additional steps.


Start by updating to the latest minor version of your current major version first (e.g. ``v5.10`` to ``v5.11``).

When running containers, you may not even need to do anything special, other than following the minor update steps below.

----

## Minor updates

!!! note ""
    
    When a new minor version of DSMR-reader is released (e.g. ``v6.0`` to ``v6.1``).

!!! abstract ""

    Note that we are using `podman-compose`, everywhere, and **not** `podman compose` (note the dash/whitespace difference). Using the latter will result in different behavior!

- Log in as the `dsmrreader` user and run:

``` shell
sudo su - dsmrreader
podman-compose pull
podman-compose up -d
```

Check in DSMR-reader if you are now running the latest version in the series.

----

## Restarting DSMR-reader

You might want or need to restart DSMR-reader manually at some time, without updating.
E.g. due to altered settings that need to be reapplied to DSMR-reader.

- Log in as the `dsmrreader` user and run:

``` shell
sudo su - dsmrreader
podman-compose up -d
```
