# Username & password

Admin and management interface require admin access. Set credentials as follows:

- Open ``compose.env`` and add ``DSMRREADER_ADMIN_USER`` and ``DSMRREADER_ADMIN_PASSWORD`` environment variables:

```yaml title="compose.env" hl_lines="1-2"
DSMRREADER_ADMIN_USER=admin
DSMRREADER_ADMIN_PASSWORD=supersecretpassword
```

- Restart the container, it will automatically run `manage.py dsmr_superuser`, which will either create or reset the admin user credentials.

```shell title="shell"
podman-compose up -d
```
