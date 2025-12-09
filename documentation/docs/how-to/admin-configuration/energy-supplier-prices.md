# Energy supplier prices

## Recalculate prices retroactively

> "I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?"

- Log in as the `dsmrreader` user and run:

``` shell
sudo su - dsmrreader
podman-compose exec /app/dsmr manage.py dsmr_stats_recalculate_prices
```
