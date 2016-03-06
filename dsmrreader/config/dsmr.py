""" DSMR Project settings. """

DSMR_SUPPORTED_DB_VENDORS = ('postgresql', 'mysql')

DSMR_BACKUP_DIRECTORY = 'backups'  # Relative to project root.
DSMR_DROPBOX_SYNC_INTERVAL = 1  # Only check for changes once per hour.

DSMR_MANAGEMENT_COMMANDS_PID_FOLDER = '/var/tmp/'
