Common error resolution: How do I recalculate prices retroactively?
===================================================================

I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?

Execute::

    sudo su - dsmr
    ./manage.py dsmr_stats_recalculate_prices
