""" DSMR Project settings. """

import pytz


# Local timezone to maintain for GUI. (<> TIME_ZONE!)
LOCAL_TIME_ZONE = pytz.timezone('CET')

DSMR_SUPPORTED_DB_VENDORS = ('postgresql', 'mysql')

DSMR_BACKUP_DIRECTORY = 'backups'  # Relative to project root.

DSMR_DROPBOX_SYNC_INTERVAL = 1  # Only check for changes once per hour.
