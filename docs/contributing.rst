Contributing
============
Would you like to contribute or help this project in any way?

P1 Telegram snapshot
--------------------
Please start by creating an issue with a snapshot of a DSMR telegram. It will help me in improving support for multiple meter vendors and home situations.

You can find the telegram by executing ``sudo supervisorctl tail -n 100 dsmr_datalogger`` on your DSMR-reader system.

*You should omit your unique meter identification*, for privacy reasons, which are the lines starting with ``0-0:96.1.1`` or ``0-1:96.1.0``, followed by the meter ID.

Feedback
--------
Also all feedback and input is, as always, very much appreciated! `Please create an issue on Github <https://github.com/dennissiemensma/dsmr-reader/issues>`_.

It doesn't matter whether you run into problems getting started in this guide or just want to get in touch, just fire away.