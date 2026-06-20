Lock migrations for a new release:

```bash
poetry run /app/src/manage.py dsmrreader_lock_migrations
```

This command writes the downgrade script to `provisioning/container/downgrade/v<version>.sh`.
Report the file path that was written and confirm the file exists.
