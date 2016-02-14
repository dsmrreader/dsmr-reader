""" DSMR Project settings. """

import pytz


# Local timezone to maintain for GUI. (<> TIME_ZONE!)
LOCAL_TIME_ZONE = pytz.timezone('CET')

DSMR_SUPPORTED_DB_VENDORS = ('postgresql', 'mysql')
