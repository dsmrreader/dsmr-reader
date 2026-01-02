# Updates

DSMR-reader update process. To see (recent) updates check the changelog.

[Changelog](../../reference/changelog.md){ .md-button .md-button--primary }
[Recent Xirixiz container updates](https://ghcr.io/xirixiz/dsmr-reader-docker){ .md-button .md-button--primary }

----

## Restarting DSMR-reader

You might want or need to restart DSMR-reader manually at some time, without updating.
E.g. due to altered settings that need to be reapplied to DSMR-reader.

- Log in as the `dsmrreader` user and run:

```shell
sudo su - dsmrreader
podman-compose up -d
```

- If no settings were changed, this will have no effect. Then run this instead:

```shell
podman-compose restart dsmr
```

----

## Minor updates (``v6.X`` to ``v6.Y``)

!!! note ""
    
    When a new minor version of DSMR-reader is released (e.g. ``v6.0`` to ``v6.1``).

!!! abstract ""

    Note that we are using `podman-compose`, everywhere, and **not** `podman compose` (note the dash/whitespace difference). Using the latter will result in different behavior!

- Log in as the `dsmrreader` user and run:

```shell
sudo su - dsmrreader
podman-compose pull
podman-compose up -d
```

Check in DSMR-reader if you are now running the latest version in the series.

----

## Major updates (``vX.*`` to ``vY.*``)

!!! note ""
    
    When a new major version of DSMR-reader is released (e.g. ``v6.x`` to ``v7.0``) you need to follow additional steps.

- Start by updating to the **latest minor version** of your current major version first (e.g. ``v5.11`` to ``v5.12``). See minor updates above.

If that works, check the [Changelog](../../reference/changelog.md) for any special instructions before updating to the next major.
Some incompatible changes may be there, e.g. unsupported database versions or featured **removed** from DSMR-reader.

- Log in as the `dsmrreader` user:

```shell
sudo su - dsmrreader
```

- Open the Compose YAML file and change the image tag to the new major version. 
    - *For example, to upgrade to DSMR-reader v7.x (in the future), change ``dsmr-reader-docker:6`` to ``dsmr-reader-docker:7``*

```yaml title="compose.yml (simplified version)" hl_lines="4"
services:
    dsmr:
        # This will always use the latest minor release within the major DSMR-reader vX version specified below (dsmr-reader-docker:X)
        image: ghcr.io/xirixiz/dsmr-reader-docker:7
```

- To apply, now run:

```shell
podman-compose up -d
```

Check in DSMR-reader if you are now running the latest version in the series.
