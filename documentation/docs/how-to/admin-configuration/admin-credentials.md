# Username & password

Admin and management interface require admin access. Set credentials as follows:

- Open ``compose.yml`` and add ``DSMRREADER_ADMIN_USER`` and ``DSMRREADER_ADMIN_PASSWORD`` environment variables under the `dsmr` service:

```yaml
# Simplified compose.yml
services:
    dsmr:
        environment:
            DSMRREADER_ADMIN_USER=admin
            DSMRREADER_ADMIN_PASSWORD=supersecretpassword
```

- Restart the container, it will automatically run `manage.py dsmr_superuser`, which will either create or reset the admin user credentials.

```shell
podman-compose restart dsmr
```
