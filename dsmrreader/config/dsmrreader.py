import dsmrreader


# Officially we only support PostgreSQL, but w/e.
DSMRREADER_SUPPORTED_DB_VENDORS = ('postgresql', 'mysql')

DSMRREADER_BACKUP_PG_DUMP = 'pg_dump'
DSMRREADER_BACKUP_MYSQLDUMP = 'mysqldump'
DSMRREADER_BACKUP_SQLITE = 'sqlite3'
DSMRREADER_REST_FRAMEWORK_API_USER = 'api-user'

DSMRREADER_MANAGEMENT_COMMANDS_PID_FOLDER = '/var/tmp/'

DSMRREADER_VERSION = dsmrreader.__version__
DSMRREADER_RAW_VERSION = dsmrreader.VERSION
DSMRREADER_USER_AGENT = 'DSMR-reader v{}'.format(DSMRREADER_VERSION)
DSMRREADER_LATEST_VERSION_FILE = 'https://raw.githubusercontent.com/dennissiemensma/dsmr-reader/v3/dsmrreader/__init__.py'

# Scheduled Process modules.
DSMRREADER_MODULE_EMAIL_BACKUP = 'dsmr_backup.services.email.run'
DSMRREADER_MODULE_AUTO_UPDATE_CHECKER = 'dsmr_backend.services.update_checker.run'
DSMRREADER_MODULE_WEATHER_UPDATE = 'dsmr_weather.services.run'
DSMRREADER_MODULE_STATS_GENERATOR = 'dsmr_stats.services.run'
DSMRREADER_MODULE_MINDERGAS_EXPORT = 'dsmr_mindergas.services.run'

# Sleep durations for infinity processes. Update these in your own config if you wish to alter them.
DSMRREADER_BACKEND_SLEEP = 1  # Will be REMOVED in v3.x+
DSMRREADER_DATALOGGER_SLEEP = 0.5  # Will be REMOVED in v3.x+
DSMRREADER_MQTT_SLEEP = 1  # Will be REMOVED in v3.x+

DSMRREADER_DROPBOX_MAX_FILE_MODIFICATION_TIME = 60 * 60 * 24 * 7
DSMRREADER_DROPBOX_SYNC_INTERVAL = 1  # Only check for changes once per hour.
DSMRREADER_DROPBOX_ERROR_INTERVAL = 12  # Skip new files for 12 hours when insufficient space in Dropbox account.

DSMRREADER_COMPACT_MAX = 1024  # Max telegrams to compact in a single run.

# Whether telegrams are logged, in base64 format. Only required for debugging.
DSMRREADER_LOG_TELEGRAMS = False  # Will be REMOVED in v3.x+

# When processes should reconnect to the DB, to ensure the connection is still there.
DSMRREADER_MAX_DATABASE_CONNECTION_SESSION_IN_SECONDS = 30 * 60

# Maximum interval allowed since the latest reading, before ringing any alarms.
DSMRREADER_STATUS_READING_OFFSET_MINUTES = 60

# The cooldown period until the next status notification will be sent.
DSMRREADER_STATUS_NOTIFICATION_COOLDOWN_HOURS = 12

# Number of queued MQTT messages the application will retain. Any excess will be purged.
DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE = 200

# Number of hours to cleanup in one run of applying retention.
DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN = 24

# Plugins.
DSMRREADER_PLUGINS = []

DSMRREADER_BUIENRADAR_API_URL = 'https://data.buienradar.nl/2.0/feed/json'
