Database: Migrate day/hour statistics (PostgreSQL)
==================================================

.. note::

    This will only work if you have access to both the previous database and the one you're using now.

- Execute on your old system/database::

    sudo su - postgres

    # Dagstatistieken uit oude database:
    echo "COPY public.dsmr_stats_daystatistics (day, total_cost, electricity1, electricity2, electricity1_returned, electricity2_returned, electricity1_cost, electricity2_cost, gas, gas_cost, average_temperature, highest_temperature, lowest_temperature, fixed_cost) FROM stdin;" > day_statistics_dump.sql
    psql -d dsmrreader -c "COPY public.dsmr_stats_daystatistics (day, total_cost, electricity1, electricity2, electricity1_returned, electricity2_returned, electricity1_cost, electricity2_cost, gas, gas_cost, average_temperature, highest_temperature, lowest_temperature, fixed_cost) TO stdout" >> day_statistics_dump.sql

    # Uurstatistieken uit oude database:
    echo "COPY public.dsmr_stats_hourstatistics (hour_start, electricity1, electricity2, electricity1_returned, electricity2_returned, gas) FROM stdin;" > hour_statistics_dump.sql
    psql -d dsmrreader -c "COPY public.dsmr_stats_hourstatistics (hour_start, electricity1, electricity2, electricity1_returned, electricity2_returned, gas) TO stdout" >> hour_statistics_dump.sql

- Transfer the files created above to your new system/database::

    /var/lib/postgres/day_statistics_dump.sql
    /var/lib/postgres/hour_statistics_dump.sql

- Execute on your new system/database::

    sudo su - postgres

    # Dagstatistieken naar nieuwe database:
    psql -f day_statistics_dump.sql -d dsmrreader
    psql -d dsmrreader
    SELECT setval(pg_get_serial_sequence('"dsmr_stats_daystatistics"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "dsmr_stats_daystatistics";

    # Uurstatistieken naar nieuwe database:
    psql -f hour_statistics_dump.sql -d dsmrreader
    psql -d dsmrreader
    SELECT setval(pg_get_serial_sequence('"dsmr_stats_hourstatistics"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "dsmr_stats_hourstatistics";

If there is any collision with dates or hours in your new database, you will see an error.
