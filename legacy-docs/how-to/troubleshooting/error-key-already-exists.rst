Common error resolution: How do I fix ``DETAIL: Key (id)=(123) already exists``?
================================================================================

This depends on the situation, but you can always try the following yourself first::

    # Note: dsmr_sqlsequencereset is only available in DSMR-reader v3.3 and higher
    sudo su - dsmr
    ./manage.py dsmr_sqlsequencereset

.. seealso::

    If it does not resolve your issue, ask for support on GitHub (see end of page).
