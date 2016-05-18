Frequently Asked Questions (FAQ)
================================

Feature/bug report
------------------
**How can I propose a feature or report a bug I've found?**

`Just create a ticket at Github <https://github.com/dennissiemensma/dsmr-reader/issues/new>`_

Recalculate prices
------------------
**I've adjusted my energy prices but there are no changes! How can I regenerate them with my new prices?**

*You can flush your statistics by executing:*

``./manage.py dsmr_stats_clear_statistics --ack-to-delete-my-data``

*The application will delete all statistics and (slowly) regenerate them in the background. Just make sure the source data is still there.*