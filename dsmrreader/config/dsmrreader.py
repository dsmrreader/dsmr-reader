import dsmrreader


# Officially we only support PostgreSQL.
DSMRREADER_SUPPORTED_DB_VENDORS = ('postgresql', 'mysql')

DSMRREADER_BACKUP_PG_DUMP = 'pg_dump'
DSMRREADER_BACKUP_MYSQLDUMP = 'mysqldump'
DSMRREADER_BACKUP_SQLITE = 'sqlite3'
DSMRREADER_REST_FRAMEWORK_API_USER = 'api-user'

DSMRREADER_MANAGEMENT_COMMANDS_PID_FOLDER = '/var/tmp/'

DSMRREADER_VERSION = dsmrreader.__version__
DSMRREADER_RAW_VERSION = dsmrreader.VERSION
DSMRREADER_LATEST_VERSION_FILE = 'https://raw.githubusercontent.com/dennissiemensma/dsmr-reader/master/dsmrreader/__init__.py'

# Scheduled Process modules.
DSMRREADER_MODULE_EMAIL_BACKUP = 'dsmr_backup.services.email.run'

# Sleep durations for infinity processes. Update these in your own config if you wish to alter them.
DSMRREADER_BACKEND_SLEEP = 1
DSMRREADER_DATALOGGER_SLEEP = 0.5
DSMRREADER_MQTT_SLEEP = 1

DSMRREADER_DROPBOX_SYNC_INTERVAL = 1  # Only check for changes once per hour.
DSMRREADER_DROPBOX_ERROR_INTERVAL = 12  # Skip new files for 12 hours when insufficient space in Dropbox account.

# Whether telegrams are logged, in base64 format. Only required for debugging.
DSMRREADER_LOG_TELEGRAMS = False

# Whether the backend process (and datalogger) reconnects to the DB after each run.
DSMRREADER_RECONNECT_DATABASE = True

# Maximum interval allowed since the latest reading, before ringing any alarms.
DSMRREADER_STATUS_READING_OFFSET_MINUTES = 60

# The cooldown period until the next status notification will be sent.
DSMRREADER_STATUS_NOTIFICATION_COOLDOWN_HOURS = 12

# Number of queued MQTT messages the application will retain. Any excess will be purged.
DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE = 100

# Number of hours to cleanup in one run of applying retention.
DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN = 24

# Retention will no longer start when this hour has passed (i.e.: 6 A.M.)
DSMRREADER_RETENTION_UNTIL_THIS_HOUR = 6

# Plugins.
DSMRREADER_PLUGINS = []

# Whether to override (disable) capabilities.
DSMRREADER_DISABLED_CAPABILITIES = []
